# Release Notes - v0.9.1

**릴리스 일자**: 2026-01-15

## 릴리즈 파이프라인 안정화 (PyPI Trusted Publishing / Token 지원)

CodeGraphMCPServer v0.9.1에서는 GitHub Actions 릴리즈 워크플로의 PyPI 배포가
Trusted Publishing(OIDC) 또는 PyPI API Token 방식으로 안정적으로 동작하도록 개선했습니다.

---

## 신규 기능
### PyPI 배포 개선
- `PYPI_API_TOKEN`이 설정되어 있으면 토큰 방식으로 배포
- `PYPI_API_TOKEN`이 없으면 Trusted Publishing(OIDC)으로 배포 시도
- GitHub Actions `environment` 의존 없이 동작하도록 정리

---

## 버전 이력

| Version | Date | Highlights | Languages | Tests |
|---------|------|------------|-----------|-------|
| v0.1.0 | 2025-11-26 | Initial: Python, TS, JS, Rust | 4 | 182 |
| v0.3.0 | 2025-11-27 | +PHP, C#, C++, HCL, Ruby, Go, Java | 11 | 286 |
| v0.4.0 | 2025-11-27 | CLI Progress Display | 11 | 286 |
| v0.5.0 | 2025-11-27 | 47x Performance (Batch DB) | 11 | 285 |
| v0.6.0 | 2025-11-27 | Background Server Management | 11 | 285 |
| v0.7.0 | 2025-11-27 | File Watch, GitHub Actions CI/CD | 12 | 308 |
| v0.9.0 | 2025-12-11 | +Kotlin, Swift, Scala, Lua | 16 | 334 |
| **v0.9.1** | **2026-01-15** | **CI: PyPI publish 안정화** | **16** | **334** |

---

## 지원 언어 (16개)

| 언어         | 확장자                      |
|--------------|-----------------------------|
| Python       | .py, .pyi                   |
| TypeScript   | .ts, .tsx                   |
| JavaScript   | .js, .jsx                   |
| Rust         | .rs                         |
| Go           | .go                         |
| Java         | .java                       |
| PHP          | .php                        |
| C#           | .cs                         |
| C/C++        | .c, .cpp, .cc, .cxx, .h, .hpp, .hxx |
| HCL          | .hcl, .tf                   |
| Ruby         | .rb                         |
| Kotlin       | .kt, .kts                   |
| Swift        | .swift                      |
| Scala        | .scala, .sc                 |
| Lua          | .lua                        |

---

## 링크

- **GitHub**: https://github.com/gaebalai/CodeGraphMCPServer
- **PyPI**: https://pypi.org/project/codegraph-mcp-server/
- **CHANGELOG**: [CHANGELOG.md](CHANGELOG.md)
