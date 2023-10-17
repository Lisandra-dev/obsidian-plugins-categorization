# Obsidian Plugins Categorization

![GitHub](https://img.shields.io/github/license/ramisedhom/obsidian-plugins-categorization)

-> [TABLE (Read only)](https://cloud.seatable.io/dtable/external-links/37f27445cf4745178e06/)
-> [IMPROVE (Need account)](https://cloud.seatable.io/dtable/links/9770a2f8544e4114b38d)

## Purpose

Considering that [Obsidian.md](https://obsidian.md) has constantly increasing number of [third-party plugins](https://github.com/obsidianmd/obsidian-releases/blob/master/community-plugins.json) by community contributions, it becomes more difficult to find the proper plugin that help me optimize my notes workflow.

Hence, I did some effort to collect Obsidian.md community plugins and categorize them one-by-one using [Airtable database](https://airtable.com/invite/l?inviteId=invZOB0AEYoqO8gri&inviteToken=d699fe9527edbed243460be2b2e561f9c467867a1145e92e81f64c8d4f4fcafb&utm_source=email). By end of June 2023, the number of plugins is hitting the limit my free account on Airtables. Hence comes the next step to move the database to [Seatable](https://cloud.seatable.io/dtable/links/eaf696faed944cbba838).

My main purpose behind this effort is to help myself and others to find the proper plugin for different personal needs after using Obsidian.md.

## Developpement

The database is fetch and completed using the package in `src/`. Each file have there own purpose, and it use the GitHub API (connected via a GitHub Tokens) to get:
- DesktopOnly
- FundingUrl (only the first link is used if an object is used)
- The last commit date. The Etag is conserved in the `ETAGS` columnn in the database to prevent multiple-fetching and killing the GitHub API. The commits date allow to tags the plugin in two development state:
  - STALE : No update in one year
  - ACTIVE : Less than one year

  After, plugin are reviewed and this state can be edited to:
  - ARCHIVED : The author looking for a new maintener or archived the repository manually, without removing it from the Obsidian Community list.
  - MAINTENANCE: No new FR will be made but bug-fix and PR will be merged.

> [!NOTE]
> You need to create an `.env` file with the following content:
> ```bash
> GITHUB_TOKEN=YOUR_GITHUB_TOKEN
> SEATABLE_API_TOKEN=YOUR_SEATABLE_API_TOKEN
> ```
> - [See here for how to get the GITHUB_TOKEN](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
> - [See here for how to get the seatable Token](https://seatable.io/en/docs/seatable-api/erzeugen-eines-api-tokens/) your Seatable API Token

## Output

[Seatable database](https://cloud.seatable.io/dtable/external-links/37f27445cf4745178e06/)

The DB have some hidden columns for developping purpose.

## Discussions

- [Plugin categorisation on Obsidian Forum](https://forum.obsidian.md/t/plugin-categorisation/13565)
- [Plugin categories on Obsidian Discord](https://discord.com/channels/686053708261228577/888107495233568778)

## Further evolution

Thanks to [Argentina Ortega Sáinz](https://github.com/argenos), this effort had been published on [Obsidian Hub](https://publish.obsidian.md/hub/02+-+Community+plugins/02+-+Community+plugins)

## Contribution

There are several ways to contribute here, either by:
  - Review, update and improve categorization on [Seatable database](https://cloud.seatable.io/dtable/links/  eaf696faed944cbba838) or in [Obsidian Hub](https://publish.obsidian.md/hub/02+-+Community+plugins/02+-+Community  +plugins),
  - Improve the python scripts shared here,
  - Suggest new features,
  - Create new scripts implementing one of the ideas in "Improvement Ideas",
  - Or may be buy me a coffee to keep me awake at midnight to continue maintaining and improving this project.

## Note

This effort required me to write python scripts that are updating the database on daily bases, and export them in readable friendly markdown format.
It also requires me to go continuously through the new plugins and categorize them manually every now and then.

This is provided to everyone for free, however if you would like to say thanks or help support continued effort, feel free to send a little my way through one of the following methods:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/I2I36CJAV)
