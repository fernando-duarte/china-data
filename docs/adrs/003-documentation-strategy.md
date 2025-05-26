# ADR-003: Documentation Strategy

## Status

✅ **Accepted** (2025-01-27)

## Context

The China Economic Data Analysis package needed a comprehensive documentation strategy to improve user
experience, developer onboarding, and long-term maintainability. The existing documentation consisted
primarily of README files and inline comments, which was insufficient for:

1. **User Onboarding**: New users struggled to understand how to use the package effectively
2. **API Discovery**: Developers couldn't easily find and understand available functions and classes
3. **Maintenance**: Documentation was scattered and often became outdated
4. **Professional Presentation**: Academic and research users expected high-quality documentation

The project required a modern documentation solution that could:

- Generate API documentation automatically from code
- Provide interactive examples and tutorials
- Support mathematical notation for economic formulas
- Integrate with the existing CI/CD pipeline
- Be maintainable and version-controlled

## Decision

We decided to implement a comprehensive documentation strategy using **MkDocs with Material theme** as the
primary documentation platform, complemented by **Sphinx for API documentation** and **doctest integration**
for interactive examples.

### Core Components

1. **MkDocs Material**: Modern, responsive documentation site
2. **mkdocstrings**: Automatic API documentation generation from Python docstrings
3. **Sphinx**: Fallback for complex API documentation needs
4. **pytest-doctestplus**: Interactive code examples with testing
5. **Architecture Decision Records (ADRs)**: Document architectural decisions
6. **Mermaid diagrams**: Visual architecture and workflow documentation

### Documentation Structure

```text
docs/
├── index.md                    # Homepage
├── getting-started/           # User onboarding
├── user-guide/               # Comprehensive guides
├── api/                      # API reference
├── development/              # Developer documentation
├── adrs/                     # Architecture decisions
├── stylesheets/              # Custom CSS
└── javascripts/              # Custom JS (MathJax)
```

## Alternatives Considered

### 1. Sphinx-only Solution

- **Pros**: Mature, powerful, excellent for API docs
- **Cons**: Steeper learning curve, less modern appearance, complex configuration
- **Verdict**: Rejected as primary solution, kept as complement

### 2. GitBook

- **Pros**: Beautiful interface, collaborative editing
- **Cons**: Proprietary platform, limited customization, cost for private repos
- **Verdict**: Rejected due to vendor lock-in

### 3. Docusaurus

- **Pros**: Modern React-based, excellent performance
- **Cons**: Requires Node.js, more complex setup, overkill for Python project
- **Verdict**: Rejected due to complexity

### 4. README-only Approach

- **Pros**: Simple, no additional dependencies
- **Cons**: Limited formatting, poor discoverability, not scalable
- **Verdict**: Rejected as insufficient

## Consequences

### Positive

1. **Improved User Experience**

   - Modern, searchable documentation site
   - Clear navigation and structure
   - Interactive code examples
   - Mobile-responsive design

2. **Automated API Documentation**

   - Always up-to-date with code changes
   - Consistent formatting and structure
   - Type hints and docstrings automatically included

3. **Better Developer Onboarding**

   - Comprehensive getting started guides
   - Architecture documentation with diagrams
   - Decision history through ADRs

4. **Enhanced Maintainability**

   - Documentation as code (version controlled)
   - CI/CD integration for automated builds
   - Broken link detection and validation

5. **Professional Presentation**
   - Suitable for academic and research contexts
   - Mathematical notation support (MathJax)
   - Citation and reference management

### Negative

1. **Increased Complexity**

   - Additional dependencies (mkdocs, sphinx, etc.)
   - More complex build process
   - Learning curve for contributors

2. **Maintenance Overhead**

   - Documentation needs to be kept in sync with code
   - Additional CI/CD pipeline steps
   - More files to maintain

3. **Build Time Impact**
   - Documentation generation adds to CI/CD time
   - Larger repository size with generated docs

### Neutral

1. **Tool Ecosystem**

   - MkDocs is Python-based, fitting well with the project
   - Material theme is actively maintained
   - Good plugin ecosystem for extensions

2. **Hosting Options**
   - Can be hosted on GitHub Pages, Netlify, or other platforms
   - Static site generation enables flexible deployment

## Implementation Notes

### Phase 1: Core Infrastructure ✅

- [x] Add documentation dependencies to `pyproject.toml`
- [x] Create `mkdocs.yml` configuration
- [x] Set up basic documentation structure
- [x] Create homepage and navigation

### Phase 2: Content Creation ✅

- [x] API documentation with mkdocstrings
- [x] User guides and tutorials
- [x] Architecture Decision Records
- [x] Getting started documentation

### Phase 3: Advanced Features

- [ ] Interactive code examples with doctest
- [ ] Mathematical notation integration
- [ ] CI/CD pipeline for documentation deployment
- [ ] Documentation testing and validation

### Configuration Details

```yaml
# mkdocs.yml key features
theme: material
plugins:
  - search
  - mkdocstrings[python]
  - mermaid2
markdown_extensions:
  - pymdownx.arithmatex # Math support
  - pymdownx.superfences # Code blocks
  - admonition # Callouts
```

### Docstring Standards

All modules must follow Google-style docstrings:

```python
def process_data(data: pd.DataFrame, alpha: float = 0.33) -> pd.DataFrame:
    """Process economic data with capital share parameter.

    Args:
        data: Input economic data with time series
        alpha: Capital share in production function (0 < alpha < 1)

    Returns:
        Processed data with calculated indicators

    Raises:
        ValueError: If alpha is not in valid range

    Example:
        >>> data = pd.DataFrame({'gdp': [100, 110, 121]})
        >>> result = process_data(data, alpha=0.33)
        >>> len(result) == len(data)
        True
    """
```

## References

- [MkDocs Material Documentation](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings Documentation](https://mkdocstrings.github.io/)
- [Architecture Decision Records](https://adr.github.io/)
- [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

## Related ADRs

- [ADR-001: Python Version Strategy](001-python-version-strategy.md) - Affects documentation build requirements
- [ADR-002: Type Checking Strategy](002-type-checking-strategy.md) - Type hints appear in generated documentation
