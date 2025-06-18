## 🌙 Contributing to Nightlight-Centralized

First off – thank you for even considering contributing to Nightlight-Centralized!
Your involvement helps make this project better, stronger, and more useful for Nightlines everywhere. 


### Why Read This?
Taking a few minutes to read these guidelines shows you care about the time and effort of the maintainers. In return, we aim to give your ideas, issues, and pull requests thoughtful consideration and clear feedback.

This guide should help you:
* Understand what contributions are welcome (and what aren't)
* Learn how to set up your development environment
* Report bugs effectively
* Submit better PRs
* Feel more confident as a first-time contributor


### 🌟 What Can I Contribute?
There are many valuable ways to contribute:
* 💡 Suggest features or improvements
* 🐛 Report bugs
* 🛠 Fix bugs or refactor code
* 🧾 Improve the documentation (README, comments, etc.)
* 📘 Write usage examples or tutorials
* ✅ Add tests to improve reliability


### 🚫 What We’re Not Looking For (Right Now)
Please don’t use the issue tracker for:
* Support requests like "How do I use Flask?" or "Why don't you use django?"
* General Nightline coordination questions unrelated to this repo.
* Code formatting
Also:
* Please don’t add features that are specific to a single Nightline, unless they are clearly useful for others too.


### 📏 Ground Rules
We’re all human here. Let’s treat each other with kindness and respect.
This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).
Technical expectations:
* ✅ Code should be clean, documented, and tested if possible.
* 🧪 Test your changes locally before submitting a PR.
* 🪟 Ensure cross-platform compatibility (Linux and macOS are enough for now).
* 📦 Keep dependencies minimal and well-justified.
* 🧠 Discuss major changes in an issue before starting a big refactor or feature.
* 🤝 Be welcoming to newcomers and encourage diverse contributors.


### Small / “obvious” fixes?
You don’t need to open an issue for things like:
* Fixing typos
* Small doc tweaks
* Adding missing imports or type hints
Just go ahead and submit a PR. 💌


### 🐞 Reporting Bugs
> [!CAUTION]  
> 🔐 Security issues: Do not open a GitHub issue. Instead report them [here](https://github.com/inflac/NightLight-Centralized/security/advisories/new) using this [Guide](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)

Please open a new issue for non security related bugs and choose the `Bug report` template in order to report it. Thank you for your contribution <3.


### ✨ Suggesting Features
Have a cool idea? Open an issue using the `Feature request` template. Excited to here your feature idea :).


### 🔍 Code Review Process
* Pull requests are reviewd as soon as possible. In general this might take 5–10 days, often faster.
* Feedback will be constructive and collaborative — feel free to ask questions!
* Inactive PRs may be closed after 3 weeks with no response, but you’re always welcome to reopen later.

Larger contributions might go through multiple rounds of discussion and require more time for the review.


### 🧑‍💻 Code & Commit Style
Use descriptive commit messages (e.g. fix(api): sanitize name param or docs: add install instructions)
* Run the linting task from `.vscode` before commiting in order to lint and format your code.
* Use type hints where necessary or cast variables if there is no other option.
* Use environment variables sparingly; most configs are hardcoded intentionally
