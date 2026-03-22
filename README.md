# Lamia Examples

A growing collection of real-world examples built with [Lamia](https://github.com/lamia-lang/lamia) — a framework for writing AI-powered scripts in plain English.

New examples are added continuously. [Star this repo](https://github.com/lamia-lang/lamia-examples/stargazers) to get notified on updates.

## What is Lamia?

Lamia is all about **preciseness** — getting 100% of the expected results, every time. You write what you want; Lamia handles the LLM calls, validates the output, and returns structured data. No guessing, no loose outputs.

If a Lamia script fails, it usually means one of two things:

- The **prompt** needs to be adjusted for the task at hand
- The **LLM model** being used isn't capable enough for that particular output

Each example ships with its own `config.yaml` that specifies the exact models the example was tested against. **Using that `config.yaml` is the recommended starting point** — it removes model variance from the equation so you can focus on understanding the example itself.

> If a script is still failing when using the example's own `config.yaml`, please [open an issue](https://github.com/lamia-lang/lamia-examples/issues).

## Examples

| Example | Description |
|---------|-------------|
| [prd_implementor](./prd_implementor/) | A virtual software engineering team that takes a PRD markdown file and implements it end-to-end — PM, groomer, developer, reviewer, and QA analyst, all orchestrated by a single `.lm` script |

## Contributing

Have a use case you'd like to see covered with Lamia? Two ways to contribute:

- **Request an example** — [open an issue](https://github.com/lamia-lang/lamia-examples/issues) describing the use case. If accepted and developed, the code will be published here. Note that it will be open sourced under the MIT license.
- **Submit an example** — [open a pull request](https://github.com/lamia-lang/lamia-examples/pulls) with your Lamia example. Each example should include its own `README.md`, `config.yaml`, and be self-contained in its own directory.

## License

[MIT](./LICENSE)
