# CHANGELOG

<!-- version list -->

## v1.7.4 (2026-04-27)

### Bug Fixes

- Serialization issue with numpy float ([#54](https://github.com/totonga/odsbox-jaquel-mcp/pull/54),
  [`10c5f6f`](https://github.com/totonga/odsbox-jaquel-mcp/commit/10c5f6f91bd2b3250aca2ca5f709e0cf22e65bfa))


## v1.7.3 (2026-04-19)

### Bug Fixes

- Add verify_certificates to avoid missspelling
  ([`eddaba8`](https://github.com/totonga/odsbox-jaquel-mcp/commit/eddaba8c9e7d68f28cc67179725b75e2adf76d5c))


## v1.7.2 (2026-04-19)

### Bug Fixes

- Example_queries must be plural
  ([`05c62e6`](https://github.com/totonga/odsbox-jaquel-mcp/commit/05c62e671199fdcf93212a36afd25387359e94ec))


## v1.7.1 (2026-04-19)

### Bug Fixes

- Adjust instructions to avoid direct script generation
  ([`a5ad1a6`](https://github.com/totonga/odsbox-jaquel-mcp/commit/a5ad1a6fe89bb3b4a9a8661a8f998641b0410ab4))


## v1.7.0 (2026-04-19)

### Bug Fixes

- Build
  ([`849a3bf`](https://github.com/totonga/odsbox-jaquel-mcp/commit/849a3bfc23dcd4923c1591a98a4866e8c79fd372))

- Fix build
  ([`8fbe159`](https://github.com/totonga/odsbox-jaquel-mcp/commit/8fbe15991c0346b1d07d94bdffdd454cfae601c6))

### Features

- Modernize environment and improve return values of entity and connection
  ([#52](https://github.com/totonga/odsbox-jaquel-mcp/pull/52),
  [`e7c8fa5`](https://github.com/totonga/odsbox-jaquel-mcp/commit/e7c8fa5fd64128a3a6ada7b589b6ca5d0b52d57b))


## v1.6.1 (2026-04-11)

### Bug Fixes

- Cleanup tools (#48) ([#49](https://github.com/totonga/odsbox-jaquel-mcp/pull/49),
  [`b815e4e`](https://github.com/totonga/odsbox-jaquel-mcp/commit/b815e4e27c90ab284089182bfc09cc2148eb0e32))


## v1.6.0 (2026-04-04)

### Features

- Add OIDC login (#46) ([#47](https://github.com/totonga/odsbox-jaquel-mcp/pull/47),
  [`8dd340c`](https://github.com/totonga/odsbox-jaquel-mcp/commit/8dd340c1e2f469fb44b9f1c89f3e1b6bc9b490ea))


## v1.5.0 (2026-03-31)

### Features

- Enhance error handling and serialization in query execution
  ([#45](https://github.com/totonga/odsbox-jaquel-mcp/pull/45),
  [`dcbd23b`](https://github.com/totonga/odsbox-jaquel-mcp/commit/dcbd23bd72898b16b3b3df4cd712ffba75c4728b))


## v1.4.0 (2026-03-29)

### Features

- Refactor and enhance logging and monitoring features
  ([#43](https://github.com/totonga/odsbox-jaquel-mcp/pull/43),
  [`484f79f`](https://github.com/totonga/odsbox-jaquel-mcp/commit/484f79f6ac53c2ee21ca666e45ae461d74a65182))


## v1.3.0 (2026-03-15)

### Bug Fixes

- Bump actions/upload-artifact from 6 to 7
  ([#38](https://github.com/totonga/odsbox-jaquel-mcp/pull/38),
  [`6536423`](https://github.com/totonga/odsbox-jaquel-mcp/commit/6536423188d6fee5faf0d44957436cee3915da4d))

### Features

- Added ods_connect_using_env ([#39](https://github.com/totonga/odsbox-jaquel-mcp/pull/39),
  [`890dd0d`](https://github.com/totonga/odsbox-jaquel-mcp/commit/890dd0dca671ffa07b992f8b28d6e59e64eb1f8d))


## v1.2.0 (2026-02-28)

### Features

- Data_read_submatrix tool now supports resampling for preview
  ([#37](https://github.com/totonga/odsbox-jaquel-mcp/pull/37),
  [`4dbed6e`](https://github.com/totonga/odsbox-jaquel-mcp/commit/4dbed6e750ab81d7dea4db311bb954bb8424f172))


## v1.1.1 (2025-12-28)

### Bug Fixes

- Update MANIFEST.in and pyproject.toml to include missing files and improve documentation
  references
  ([`4dd47f4`](https://github.com/totonga/odsbox-jaquel-mcp/commit/4dd47f4e00e8419a7448c293dd5479335aff6fc7))

### Refactoring

- Refactor code generation and resource management with Jinja2 templates
  ([#33](https://github.com/totonga/odsbox-jaquel-mcp/pull/33),
  [`a8c68df`](https://github.com/totonga/odsbox-jaquel-mcp/commit/a8c68df3a3083cb8cf2a400185b18d1829c8aff9))


## v1.1.0 (2025-12-27)

### Continuous Integration

- Migrate pre-commit config to current stage naming conventions
  ([`01f994c`](https://github.com/totonga/odsbox-jaquel-mcp/commit/01f994cf8c0a73dee3f3de548afcc13ecaa5caa5))

### Features

- Add picture
  ([`0ff2f29`](https://github.com/totonga/odsbox-jaquel-mcp/commit/0ff2f2996f25541821ac2fa6636e54edb790cb01))


## v1.0.5 (2025-12-27)

### Bug Fixes

- Added missing tag
  ([`ffb9af8`](https://github.com/totonga/odsbox-jaquel-mcp/commit/ffb9af8ca88235fa84647b29fd4fd523b85923c7))


## v1.0.4 (2025-12-27)

### Bug Fixes

- Upload only once
  ([`c5d5213`](https://github.com/totonga/odsbox-jaquel-mcp/commit/c5d5213ff8ce78270eb2a9cd8491552188cbde6d))


## v1.0.3 (2025-12-27)

### Bug Fixes

- Artifacts are missing at release
  ([`2f0ad2d`](https://github.com/totonga/odsbox-jaquel-mcp/commit/2f0ad2d0435b008ba414bd9901642b0c90bcb124))


## v1.0.2 (2025-12-27)

### Bug Fixes

- Updated mcp server.json
  ([`0bc27dd`](https://github.com/totonga/odsbox-jaquel-mcp/commit/0bc27ddd7d5bb6e2ab649e2f632da8ca0c25b089))


## v1.0.1 (2025-12-27)

### Bug Fixes

- Ensure build dependencies are installed before rebuilding distributions
  ([`61941ba`](https://github.com/totonga/odsbox-jaquel-mcp/commit/61941baafb0fb9d2c01905d1620f8cc7fdae4f5e))


## v1.0.0 (2025-12-27)

### Bug Fixes

- No 1.0 release
  ([`0f11cbe`](https://github.com/totonga/odsbox-jaquel-mcp/commit/0f11cbec009a8f85b2693fe6a00189632aa6d169))

- Python-semantic-release/python-semantic-release@v10.5.3
  ([`5060472`](https://github.com/totonga/odsbox-jaquel-mcp/commit/5060472465460ddf6316d505eaaa05d55ddfdd2f))

### Continuous Integration

- Rebuild to have the right version
  ([`d221e1f`](https://github.com/totonga/odsbox-jaquel-mcp/commit/d221e1febabedaacc05382ea3eeaffddc0268ec7))

### Features

- Add pre-commit hooks and CI validation
  ([`3a84859`](https://github.com/totonga/odsbox-jaquel-mcp/commit/3a8485969e59a3b2d0ed3472cda11851070066c4))

- Rename tools and some other cleanup
  ([`cf8f666`](https://github.com/totonga/odsbox-jaquel-mcp/commit/cf8f666726c717cd45a835a7801e5caa52110aab))


## v0.5.0 (2025-12-27)

### Bug Fixes

- Python-semantic-release/python-semantic-release@v10.5.3
  ([`5060472`](https://github.com/totonga/odsbox-jaquel-mcp/commit/5060472465460ddf6316d505eaaa05d55ddfdd2f))

### Features

- Add pre-commit hooks and CI validation
  ([`3a84859`](https://github.com/totonga/odsbox-jaquel-mcp/commit/3a8485969e59a3b2d0ed3472cda11851070066c4))

- Rename tools and some other cleanup
  ([`cf8f666`](https://github.com/totonga/odsbox-jaquel-mcp/commit/cf8f666726c717cd45a835a7801e5caa52110aab))


## v0.4.0 (2025-12-25)

### Bug Fixes

- Bump actions/upload-artifact from 5 to 6
  ([`37bae0f`](https://github.com/totonga/odsbox-jaquel-mcp/commit/37bae0f6151eab3a9aa04c7cfb149c2ad918572e))


## v0.3.12 (2025-12-04)

### Features

- Add support for dynamic entity schema templates and resource template listing
  ([`46d55e6`](https://github.com/totonga/odsbox-jaquel-mcp/commit/46d55e6aa7fd23f70898d65d28ce757bdff3678d))


## v0.3.11 (2025-12-04)

### Refactoring

- Update read_resource to accept AnyUrl type for URI
  ([`1e857c1`](https://github.com/totonga/odsbox-jaquel-mcp/commit/1e857c148fc819620f88d50c6c6c1b01bd2b45dc))


## v0.3.10 (2025-12-04)

### Refactoring

- Update read_resource to return a list of resource content items
  ([`63fc1a0`](https://github.com/totonga/odsbox-jaquel-mcp/commit/63fc1a0751aad127ac2f8fc1a495d2fb1435b97f))


## v0.3.9 (2025-12-04)

### Refactoring

- Update read_resource to return TextResourceContents with mimeType
  ([`afb3850`](https://github.com/totonga/odsbox-jaquel-mcp/commit/afb3850ffd1b013e8f69fd10ed7d2d1dd908a01d))


## v0.3.8 (2025-12-04)


## v0.3.7 (2025-12-04)


## v0.3.6 (2025-12-01)


## v0.3.5 (2025-11-30)


## v0.3.4 (2025-11-27)


## v0.3.2 (2025-11-27)

### Bug Fixes

- Bump actions/checkout from 5 to 6 ([#13](https://github.com/totonga/odsbox-jaquel-mcp/pull/13),
  [`67c6637`](https://github.com/totonga/odsbox-jaquel-mcp/commit/67c66374098005eaf746e0de82746c5c0b25e5d5))


## v0.3.1 (2025-11-25)


## v0.3.0 (2025-11-23)


## v0.2.14 (2025-11-23)


## v0.2.12 (2025-11-22)

### Bug Fixes

- Bump actions/checkout from 4 to 5
  ([`c60daa0`](https://github.com/totonga/odsbox-jaquel-mcp/commit/c60daa0bb6826be52948640a955543b8029b0e66))

- Bump actions/setup-python from 4 to 6
  ([`3b75a4b`](https://github.com/totonga/odsbox-jaquel-mcp/commit/3b75a4bb02804be9a817ebb7560aa6c2f0aafa46))

- Bump actions/upload-artifact from 4 to 5
  ([`b94c6f1`](https://github.com/totonga/odsbox-jaquel-mcp/commit/b94c6f1f06fc838191d69f1e9d9a24a004ed4d43))

- Bump softprops/action-gh-release from 1 to 2
  ([`2e8d0b9`](https://github.com/totonga/odsbox-jaquel-mcp/commit/2e8d0b918bee232a859776223737db6f6f5c0cc8))


## v0.2.11 (2025-11-19)

- Initial Release
