from dotenv import load_dotenv



# bot.py
from dalle_mini import DalleBartProcessor
from functools import partial
from flax.jax_utils import replicate
import os
import io
import discord
import nest_asyncio
import re
import jax
import jax.numpy as jnp
from dalle_mini import DalleBart, DalleBartProcessor
from vqgan_jax.modeling_flax_vqgan import VQModel
from transformers import CLIPProcessor, FlaxCLIPModel
import random
from flax.training.common_utils import shard_prng_key
import numpy as np
from PIL import Image
from tqdm.notebook import trange


load_dotenv()
TOKEN = os.getenv('TOKEN')

nest_asyncio.apply()

client = discord.Client()

# dalle-mega
# DALLE_MODEL = "dalle-mini/dalle-mini/mega-1:latest"  # can be wandb artifact or 🤗 Hub or local folder or google bucket
DALLE_COMMIT_ID = None
# if the notebook crashes too often you can use dalle-mini instead by uncommenting below line
DALLE_MODEL = "dalle-mini/dalle-mini/mini-1:v0"
# VQGAN model
VQGAN_REPO = "dalle-mini/vqgan_imagenet_f16_16384"
VQGAN_COMMIT_ID = "e93a26e7707683d349bf5d5c41c5b0ef69b677a9"

# Model references
# check how many devices are available
jax.local_device_count()

# Load models & tokenizer
# Load dalle-mini
model, params = DalleBart.from_pretrained(
    DALLE_MODEL, revision=DALLE_COMMIT_ID, dtype=jnp.float16, _do_init=False
)

# Load VQGAN
vqgan, vqgan_params = VQModel.from_pretrained(
    VQGAN_REPO, revision=VQGAN_COMMIT_ID, _do_init=False
)


params = replicate(params)
vqgan_params = replicate(vqgan_params)

# model inference


@partial(jax.pmap, axis_name="batch", static_broadcasted_argnums=(3, 4, 5, 6))
def p_generate(
    tokenized_prompt, key, params, top_k, top_p, temperature, condition_scale
):
    return model.generate(
        **tokenized_prompt,
        prng_key=key,
        params=params,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
        condition_scale=condition_scale,
    )

    # decode image


@partial(jax.pmap, axis_name="batch")
def p_decode(indices, params):
    return vqgan.decode_code(indices, params=params)




processor = DalleBartProcessor.from_pretrained(
    DALLE_MODEL, revision=DALLE_COMMIT_ID)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


def get_img(input):
        # create a random key
    seed = random.randint(0, 2**32 - 1)
    key = jax.random.PRNGKey(seed)

    prompts = [
        input,
    ]

    tokenized_prompts = processor(prompts)

    tokenized_prompt = replicate(tokenized_prompts)

    # number of predictions per prompt
    n_predictions = 1

    # We can customize generation parameters (see https://huggingface.co/blog/how-to-generate)
    gen_top_k = None
    gen_top_p = None
    temperature = None
    cond_scale = 10.0


    print(f"Prompts: {prompts}\n")
    # generate images
    images = []
    for i in trange(max(n_predictions // jax.device_count(), 1)):
        # get a new key
        key, subkey = jax.random.split(key)
        # generate images
        encoded_images = p_generate(
            tokenized_prompt,
            shard_prng_key(subkey),
            params,
            gen_top_k,
            gen_top_p,
            temperature,
            cond_scale,
        )

        # remove BOS
        encoded_images = encoded_images.sequences[..., 1:]
        # decode images
        from IPython.display import display

        decoded_images = p_decode(encoded_images, vqgan_params)
        decoded_images = decoded_images.clip(
            0.0, 1.0).reshape((-1, 256, 256, 3))
        for decoded_img in decoded_images:
            img = Image.fromarray(np.asarray(
                decoded_img * 255, dtype=np.uint8))
            images.append(img)
            return img
            display(img)

            print()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if '#BotMeme' in message.content:
        # response = discord.File(open(img))
        ini_string = message.content
        input = re.sub('#BotMeme', '', ini_string)

        img = get_img(input)
        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        file = discord.File(fp=arr, filename='image.png')
        await message.channel.send(file=file)


client.run(TOKEN)

