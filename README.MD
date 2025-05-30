# EPCompatChecker

Check compatibility of Windows builds with ExplorerPatcher releases.

EPCompatChecker queries the [ExplorerPatcher GitHub releases](https://github.com/valinet/ExplorerPatcher/releases) and finds which versions are compatible with a specified Windows build. It can also auto-detect your current Windows build version.

## Features

- Query ExplorerPatcher GitHub releases for compatibility info  
- Auto-detect current Windows build version  
- Support for GitHub tokens to avoid rate limiting  
- Shows links to the compatible releases

## Usage

After running the program you can:

- Enter a Windows build version (e.g. `22631.5335`) manually or use **Auto Detect** to get your current build version.  
- Click **Check Compatibility** to see matching ExplorerPatcher releases.  
- Optionally set a GitHub token to increase API limits and avoid rate limiting.

# Building

Run `.\build.bat` in a terminal to install required dependencies and build to an executable