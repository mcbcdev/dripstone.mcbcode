# dripstone

an ai that actually knows bedrock edition.

## what is this?

need help building minecraft bedrock mods? dripstone has your back. it's got access to your projects (if you give it permission ofc), knows the [wiki.bedrock.dev](https://wiki.bedrock.dev) inside and out, and actually understands what it's talking about instead of just hallucinating random block ids.

## features

- **mcbCode project access** — connect up to 3 of your projects and let the ai dig through them
- **wiki.bedrock.dev integration** — searches the wiki like it's been living there (up to 12 page searches, 9000 chars per read because we're not savages)
- **actually competent** — trained to not be dumb about bedrock specifically
- **live and breathing** — built into [mcbcode.com/dripstone](https://mcbcode.com/dripstone), no installation needed

## try it out

just go to [mcbcode.com/dripstone](https://mcbcode.com/dripstone) and talk minecraft bedrock at it about your mod ideas. it'll figure it out.

## how it works

this repo holds the guts of dripstone:

- **system-prompt.md** — the personality and knowledge base that makes it tick
- **limits.json** — rate limits and boundaries so it doesn't go completely feral
- **blacklist.json** — pages we blocked because they're either broken or chaotic

---

built by [mcbCode](https://github.com/mcbcdev) for people who think bedrock edition modding should be easier
