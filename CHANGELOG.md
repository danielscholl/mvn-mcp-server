# Changelog

## [2.2.0](https://github.com/danielscholl/mvn-mcp-server/compare/v2.1.0...v2.2.0) (2025-10-15)


### ✨ Features

* **security:** Implement Maven profile-based security scanning ([#28](https://github.com/danielscholl/mvn-mcp-server/issues/28)) ([d7eb27e](https://github.com/danielscholl/mvn-mcp-server/commit/d7eb27ef4c048492224e03c024f4f31685f395e5))


### 🔧 Miscellaneous

* **deps:** Bump astral-sh/setup-uv from 6 to 7 ([#27](https://github.com/danielscholl/mvn-mcp-server/issues/27)) ([b177353](https://github.com/danielscholl/mvn-mcp-server/commit/b1773533adc41e7e50879e5a0ffed17780f85028))
* **deps:** Bump github/codeql-action from 3 to 4 ([#26](https://github.com/danielscholl/mvn-mcp-server/issues/26)) ([725f88c](https://github.com/danielscholl/mvn-mcp-server/commit/725f88c52cf03e19e25879f37a13d47ec7b01bac))

## [2.1.0](https://github.com/danielscholl/mvn-mcp-server/compare/v2.0.1...v2.1.0) (2025-10-05)


### ✨ Features

* **deps:** Update core dependencies and align documentation ([#24](https://github.com/danielscholl/mvn-mcp-server/issues/24)) ([8c7434c](https://github.com/danielscholl/mvn-mcp-server/commit/8c7434cfd9dde1243891079f7a57892ee8a00921))

## [2.0.1](https://github.com/danielscholl/mvn-mcp-server/compare/v2.0.0...v2.0.1) (2025-10-05)


### 🐛 Bug Fixes

* **ci:** Handle push events in security workflow checkouts ([caaf1e9](https://github.com/danielscholl/mvn-mcp-server/commit/caaf1e98b10cd6a8a01e7961a5e7f037f2c62f2d))


### 📚 Documentation

* **readme:** Improve quick start section and installation flow ([#23](https://github.com/danielscholl/mvn-mcp-server/issues/23)) ([f0849ce](https://github.com/danielscholl/mvn-mcp-server/commit/f0849cef54a763707a9f19e0b32d07528af35239))

## [2.0.0](https://github.com/danielscholl/mvn-mcp-server/compare/v1.1.1...v2.0.0) (2025-10-05)


### ⚙️ Continuous Integration

* **security:** Add pull_request_target support for fork PR scanning ([#20](https://github.com/danielscholl/mvn-mcp-server/issues/20)) ([34e72bb](https://github.com/danielscholl/mvn-mcp-server/commit/34e72bb0425dfa053cbd70f253aeabb8f2bfbeb6))

## [1.1.1](https://github.com/danielscholl/mvn-mcp-server/compare/v1.1.0...v1.1.1) (2025-10-04)


### ⚙️ Continuous Integration

* **release:** Add --system flag to uv pip install commands ([6f55f19](https://github.com/danielscholl/mvn-mcp-server/commit/6f55f19f64d87eb60559ab310a418bf8ca04d8d3))
* **release:** Fix build command by removing uv run prefix ([fdff957](https://github.com/danielscholl/mvn-mcp-server/commit/fdff957460654994446915f3fcec049a38438355))
* **release:** Fix uv build system flag ([4661f29](https://github.com/danielscholl/mvn-mcp-server/commit/4661f29e146704becae93089285c33bd000c6fb4))
* **release:** Remove uv run prefix from build commands ([f3530ef](https://github.com/danielscholl/mvn-mcp-server/commit/f3530efb56e8a0eca1dfb62c409dce27f0a8a9bf))

## [1.1.0](https://github.com/danielscholl/mvn-mcp-server/compare/v1.0.0...v1.1.0) (2025-10-04)


### ✨ Features

* **ci:** Add manual PyPI publish workflow ([73a9614](https://github.com/danielscholl/mvn-mcp-server/commit/73a96144c54dcac9171879239fd8df15cc630e12))


### 🔧 Miscellaneous

* **ci:** Add manual PyPI publish workflow with automatic release support ([c71fb48](https://github.com/danielscholl/mvn-mcp-server/commit/c71fb48fec0739195a18b02b9ec40b7de5ecd006))

## [1.0.0](https://github.com/danielscholl/mvn-mcp-server/compare/v0.2.0...v1.0.0) (2025-10-04)


### ⚠ BREAKING CHANGES

* Establishes v1.0.0 release as production-ready with official publishing strategy. Server is now ready for public distribution via PyPI and MCP Registry.

### ✨ Features

* Add comprehensive publishing strategy ([05807a9](https://github.com/danielscholl/mvn-mcp-server/commit/05807a958ec597fcd8708b61c80ebfbe1e6eaea7))


### 🐛 Bug Fixes

* **ci:** Correct cyclonedx-py command syntax in SBOM generation ([c0a999e](https://github.com/danielscholl/mvn-mcp-server/commit/c0a999eb5feff524051f91689e301e527f1f35d3))
* **ci:** Handle security workflow and test result format compatibility ([6cf3ea6](https://github.com/danielscholl/mvn-mcp-server/commit/6cf3ea6c49c836d78c353131fd878af3cbffb37f))


### 📚 Documentation

* Consolidate and reorganize documentation structure ([18725b8](https://github.com/danielscholl/mvn-mcp-server/commit/18725b8d9faccf49848ce09a43506498a8b0d965))
* Convert benefits to callout and remove redundant sections ([5616a2c](https://github.com/danielscholl/mvn-mcp-server/commit/5616a2c2a851375d159fb5a702294262fa02c3a4))
* Convert benefits to callout and remove redundant sections ([b97a31c](https://github.com/danielscholl/mvn-mcp-server/commit/b97a31c9b8959abf8e492897deab2e9dd3de1c39))
* Fix documentation inaccuracies for v1.0.0 release ([facf7f7](https://github.com/danielscholl/mvn-mcp-server/commit/facf7f7e270faf38eff89330172e5797a86b1cb6))
* Fix documentation inaccuracies for v1.0.0 release ([537fe66](https://github.com/danielscholl/mvn-mcp-server/commit/537fe66df3819f81857c0f33a84f4f9ac207c9b7))
* Further streamline README ([29a02f7](https://github.com/danielscholl/mvn-mcp-server/commit/29a02f72ef1d740224887a83970719152f02903c))
* Improve key benefits formatting in README ([53e8404](https://github.com/danielscholl/mvn-mcp-server/commit/53e840467b55d29f5af916fb50e6b3688bbbfd0c))
* Polish README based on review feedback ([008c74a](https://github.com/danielscholl/mvn-mcp-server/commit/008c74a6d0e39a4ccacfe5c6483a513c7150c55f))
* Polish README for PyPI release ([4168f17](https://github.com/danielscholl/mvn-mcp-server/commit/4168f17b47e40bed6138ec27dbbe5224062a4b1c))
* Remove redundant server workflow description from README ([24f642b](https://github.com/danielscholl/mvn-mcp-server/commit/24f642b9055779055743ef2f4d4d6e734300bfb3))
* Remove redundant server workflow description from README ([6dafafe](https://github.com/danielscholl/mvn-mcp-server/commit/6dafafef87cff9db26b36efd23164242ce433f76))
* Restructure documentation for user-first experience ([5b5d92d](https://github.com/danielscholl/mvn-mcp-server/commit/5b5d92d5ffd8855aa10e5bb790691c04dd5317c3))
* Restructure README to prioritize published installation ([a95daaf](https://github.com/danielscholl/mvn-mcp-server/commit/a95daaf2718931a9c4e9db83c14d84165171d056))
* Streamline README and optimize workflows ([f9c991d](https://github.com/danielscholl/mvn-mcp-server/commit/f9c991db0596343b3346b3c9d79e96f6023ca0eb))
* Streamline README and optimize workflows ([6481c00](https://github.com/danielscholl/mvn-mcp-server/commit/6481c00501a20e4f0478419a6900ba9ac9dbc694))


### 💎 Styles

* Format logger.debug with black ([20aa7b9](https://github.com/danielscholl/mvn-mcp-server/commit/20aa7b9b1e82ac74af9ec76a2998b4d352aabf88))


### 🔧 Miscellaneous

* Add __init__.py to release-please version tracking ([6e2b837](https://github.com/danielscholl/mvn-mcp-server/commit/6e2b8374e562f3570fea0db3e99419da94820167))
* Configure release-please to update server.json ([df83837](https://github.com/danielscholl/mvn-mcp-server/commit/df83837bfedfc98278811546a360bbd79c68ebf8))


### ⚙️ Continuous Integration

* Remove paths-ignore filters from workflow triggers ([ee9cdee](https://github.com/danielscholl/mvn-mcp-server/commit/ee9cdee088efec60a378655e6b93bd69ed63940b))
