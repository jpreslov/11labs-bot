# ElevenLabs Discord Bot

> Requires you add your own Discord token and ElevenLabs API key

## `/listvoices`
List custom (cloned) voices specific to your account

## `/gen`
Generate audio from a custom voice

Params:
- `voice_name`: Must be an option returned from `/listvoices`
- `prompt`: The text you want the model to say
- `stability`: A tenth decimal value 0 - 1 (default = 0.5; lower is funnier)
- `similarity`: A tenth decimal vlaue 0 - 1 (default = 0.6; higher is "more similar" to source material)

## `/vcgen`
- Does not work - if anyone knows how to implement this, please help!
