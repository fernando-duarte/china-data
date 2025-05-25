## Review Criteria

### 1. Best Practices
- **Industry Standards:** All code follows current Python guidelines and latest official documentation standards
- **Tool Configuration:** Development tools (linters, formatters, testers) use latest stable versions and recommended settings
- **Code Quality:** Consistent application of clean code principles across all modules and functions
- **Documentation Standards:** All documentation follows current best practices from official sources and style guides
- **Security Compliance:** Code adheres to latest security best practices and vulnerability prevention guidelines
- **Use Online Resources for Latest Updates:** Check relevant documentation and guides online to ensure most current best practices for codebase's dependencies


## Project Management

### 1. Code Organization and Consistency
- **Centralized Configuration:** `config.py` serves as single source for all settings, constants, and parameters
- **No Code Duplication:** Column mappings, indicators, and parameters defined once and reused throughout codebase
- **Modular Structure:** Utility functions organized in dedicated modules with clear separation of concerns
- **Path Management:** Centralized path handling in `path_constants.py` with consistent usage patterns
- **Data Flow:** Clear import structure with no circular dependencies

### 2. Complete Documentation
- **Updated README.md:** `README.md` files reflect current state of the codebase (do not add or remove anything from these files, just update if needed)
- **Module Docstrings:** Every Python file has clear module-level docstring explaining purpose and functionality
- **Function Documentation:** All functions have docstrings with parameter descriptions, return values, and usage examples
- **Inline Comments:** Explanatory comments for complex logic and business rules
- **Version Consistency:** All documentation reflects current codebase state and implementation

### 3. Dependency Management
- **Cleaned Requirements:** Removed unused dependencies, organized by functional category in `requirements.txt`
- **Development Dependencies:** Development tools separated into `dev-requirements.txt` for clean production installs
- **Verified Usage:** All listed packages are actively used and necessary for codebase functionality
- **Version Pinning:** Dependencies pinned to compatible versions to ensure reproducible builds
- **Minimal Footprint:** Only essential packages included to reduce attack surface and complexity

### 4. Code Quality Tools
- **Linting Configuration:** flake8 configured with project-specific rules in `.flake8` file
- **Code Formatting:** Black formatter with 120-character line limit for consistent style
- **Import Organization:** isort configured for Black-compatible import sorting and grouping
- **Testing Framework:** pytest with comprehensive test suite and coverage reporting
- **Integration:** All tools configured in `pyproject.toml` with consistent project-wide settings

### 5. Magic Values and Constants
- **No Magic Numbers:** All numeric constants defined in `config.py` with descriptive names
- **String Constants:** Magic strings avoided, all text constants centrally defined
- **CLI Parameters:** Command-line variables have single source of truth in configuration
- **Default Values:** All default values explicitly defined and documented in central location
- **Maintainability:** Constants grouped logically with clear naming conventions

## Technical Standards

### 6. File Length Limit (200 lines)
- **Enforced Maximum:** No Python file exceeds 200 lines to ensure readability and maintainability
- **Function Granularity:** Complex functions broken into smaller, focused helper functions
- **Module Responsibility:** Each module has single, well-defined responsibility preventing bloat

### 7. No Linting Issues
- **Flake8 Compliance:** All code passes flake8 checks with 120-character line limit configuration
- **Import Cleanliness:** No unused imports, all imports properly organized and necessary
- **Code Style:** Consistent whitespace, indentation, and formatting throughout codebase
- **Variable Usage:** No unused variables, all declared variables serve a purpose
- **String Formatting:** Proper f-string usage, no deprecated string formatting methods

### 8. Consistent File Formatting
- **Black Formatting:** All Python files consistently formatted with Black (120-character limit)
- **Import Sorting:** isort maintains consistent import order compatible with Black formatting
- **Configuration Files:** `.flake8` and `pyproject.toml` ensure tool consistency across development environments
- **Line Endings:** Consistent line and file endings and encoding across all project files
- **Whitespace Management:** No trailing whitespace, consistent indentation levels

### 9. Math Formatting
- **Markdown Compatibility:** All markdown files with mathematical expressions compile correctly with pandoc to PDF
- **Screen Display:** Mathematical formulas render clearly and attractively in terminal/screen output
- **Consistency:** Mathematical notation consistent across entire codebase and documentation
- **Source Authority:** `china_growth_model.md` serves as definitive source for all formulas and mathematical models

### 10. Type Checking
- **mypy Configuration:** Type checker configured in `pyproject.toml` with strict settings enabled
- **Function Signatures:** All public functions have complete type hints for parameters and return values
- **Zero Error Tolerance:** mypy runs with zero type errors on all production code
- **Generic Types:** Proper use of generic types and type variables where appropriate
- **Import Typing:** Consistent use of typing module imports and modern type syntax

## Process and Quality

### 11. Security
- **No Dangerous Code Execution:** Verified no use of `eval()`, `exec()`, or `pickle.loads()` functions
- **SSL/TLS Verification:** All HTTP requests use default SSL verification (requests library default behavior)
- **Network Timeouts:** All network operations have appropriate timeouts (30 seconds for downloads)
- **Input Validation:** Command-line arguments validated with proper ranges and type checking
- **Secure File Handling:** Temporary files use secure permissions (0o600) and automatic cleanup
- **Error Handling:** Error messages don't expose sensitive system information
- **Data Integrity:** SHA-256 hash verification for IMF data files

### 12. Testing
- **High Coverage:** Test coverage maintained at 95% or higher for all production code
- **Test Reliability:** All tests pass consistently (allow failures only when external sources are unavailable)
- **Descriptive Names:** Test functions have clear, descriptive names indicating what they verify
- **Comprehensive Docstrings:** Test functions documented with purpose and expected behavior
- **HTML Reports:** pytest-html configured for detailed test reporting and coverage analysis

### 13. Error Handling
- **Logging Standards:** All error reporting uses logging framework, never `print()` statements
- **Consistent Patterns:** Error handling patterns standardized across all modules and functions
- **Informative Messages:** Error messages provide sufficient context without exposing sensitive information
- **Exception Hierarchy:** Custom exception classes used for different error categories
- **Graceful Degradation:** System handles errors gracefully with appropriate fallback behavior

### 14. Modularity and Maintainability
- **Clear Module Structure:** Organized directory structure
- **Single Responsibility:** Each module focuses on one specific aspect of functionality
- **Loose Coupling:** Modules interact through well-defined interfaces with minimal dependencies
- **High Cohesion:** Related functionality grouped together within appropriate modules
- **Testability:** Module design facilitates easy unit testing and mocking
