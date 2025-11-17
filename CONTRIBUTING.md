# Contributing to Fluent

First off, thank you for considering contributing to this project! 🎉

This document provides guidelines for contributing to Fluent. Following these guidelines helps maintain code quality and makes the contribution process smooth for everyone.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Guidelines](#development-guidelines)
- [Submission Guidelines](#submission-guidelines)
- [Community](#community)

---

## 🤝 Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. By participating, you are expected to uphold this code:

- **Be respectful** - Treat everyone with respect and consideration
- **Be collaborative** - Work together and help each other
- **Be constructive** - Provide helpful feedback
- **Be inclusive** - Welcome contributors from all backgrounds
- **Be patient** - Remember that everyone is learning

---

## 🚀 Getting Started

### Prerequisites

- [Claude Code](https://code.claude.com) installed
- Git for version control
- Basic understanding of:
  - JSON data structures
  - Markdown formatting
  - YAML frontmatter
  - Language learning principles (helpful but not required)

### Setting Up Development Environment

1. **Fork the repository:**
   ```bash
   git clone https://github.com/m98/fluent.git
   cd fluent
   ```

2. **Create a branch for your work:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Test the system:**
   ```bash
   claude
   /setup
   ```

4. **Make your changes and test thoroughly**

---

## 💡 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When filing a bug report, include:**
- Clear, descriptive title
- Exact steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Your environment (OS, Claude Code version)
- Error messages or logs

**Use this template:**
```markdown
**Bug Description:**
A clear description of what the bug is.

**To Reproduce:**
1. Run command '...'
2. Enter '...'
3. See error

**Expected Behavior:**
What you expected to happen.

**Screenshots:**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS 14.0]
- Claude Code Version: [e.g. 1.0.0]
- Target Language: [e.g. Spanish]
```

### ✨ Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**When suggesting an enhancement:**
- Use a clear, descriptive title
- Provide detailed description of suggested enhancement
- Explain why this enhancement would be useful
- List examples of how it would work
- Include mockups if applicable

### 🌐 Adding Language-Specific Features

Want to add optimizations for a specific language? Great!

**Steps:**
1. Create `languages/{language-code}/` directory
2. Add language-specific grammar rules
3. Add common error patterns
4. Add frequency lists
5. Document in `languages/{language-code}/README.md`

**Example structure:**
```
languages/
├── es-ES/           # Spanish
│   ├── grammar-rules.json
│   ├── common-errors.json
│   ├── frequency-list.json
│   └── README.md
├── fr-FR/           # French
│   └── ...
└── ja-JP/           # Japanese
    └── ...
```

### 📚 Improving Documentation

Documentation improvements are always welcome!

**Areas to contribute:**
- Clarifying existing docs
- Adding examples
- Fixing typos
- Adding translations
- Creating tutorials
- Recording video guides

### 🎨 Enhancing UI/UX

Contributions to improve the learning experience:
- Better progress visualizations
- More engaging feedback messages
- Clearer error messages
- Improved statistics display

---

## 🛠️ Development Guidelines

### Code Style

**Markdown Files:**
- Use consistent heading hierarchy
- Include code blocks with language tags
- Use tables for structured data
- Keep lines under 120 characters when possible

**JSON Files:**
- Use 2-space indentation
- Include comments (where supported)
- Validate JSON structure
- Use meaningful key names

**Command Files:**
- Include YAML frontmatter
- Clear step-by-step instructions
- Use consistent formatting
- Include examples

### Commit Messages

Follow these conventions:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(vocab): Add image-based vocabulary exercises

- Implement image loading
- Add image-to-word matching
- Update vocab command

Closes #123
```

```
fix(spaced-repetition): Correct SM-2 interval calculation

The easiness factor was not being updated correctly
when quality score was below 3.

Fixes #456
```

### Testing Guidelines

**Before submitting, test:**
- Run `/setup` with different languages
- Test all slash commands
- Verify data is saved correctly
- Check spaced repetition scheduling
- Test edge cases (empty data, invalid input)
- Ensure backwards compatibility

**Testing checklist:**
```markdown
- [ ] /setup completes successfully
- [ ] /learn session works
- [ ] /review shows correct items
- [ ] /vocab tracks correctly
- [ ] /writing provides feedback
- [ ] /speaking records patterns
- [ ] /reading tests comprehension
- [ ] /progress shows statistics
- [ ] Data files update correctly
- [ ] Hooks trigger as expected
```

---

## 📝 Submission Guidelines

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes:**
   - Write clear, commented code
   - Follow style guidelines
   - Add/update tests
   - Update documentation

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

4. **Push to your fork:**
   ```bash
   git push origin feature/my-new-feature
   ```

5. **Open a Pull Request:**
   - Use descriptive title
   - Reference related issues
   - Describe changes in detail
   - Include screenshots if applicable
   - List any breaking changes

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested with multiple languages
- [ ] All slash commands work
- [ ] Data tracking verified
- [ ] No regressions found

## Screenshots (if applicable)


## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Related issues referenced

## Additional Notes
Any additional information.
```

### Review Process

1. **Maintainer review** - A maintainer will review your PR
2. **Feedback** - Address any requested changes
3. **Approval** - Once approved, your PR will be merged
4. **Recognition** - You'll be added to contributors list!

---

## 🏆 Recognition

Contributors are recognized in several ways:

- Listed in README.md contributors section
- Mentioned in release notes
- Added to CONTRIBUTORS.md
- Special badges for significant contributions

---

## 💬 Community

### Getting Help

- 💬 **GitHub Discussions** - Ask questions, share ideas
- 🐛 **GitHub Issues** - Report bugs, request features
- 📧 **Email** - For sensitive issues
- 📖 **Documentation** - Check the docs first

### Communication Guidelines

- **Be patient** - Maintainers are volunteers
- **Be specific** - Provide details and examples
- **Be constructive** - Focus on solutions
- **Be respectful** - Treat everyone kindly

---

## 📚 Additional Resources

### Learning Resources

- [SM-2 Algorithm](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)
- [CEFR Levels](https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions)
- [Spaced Repetition Research](https://www.gwern.net/Spaced-repetition)
- [Claude Code Docs](https://code.claude.com/docs)

### Project Resources

- [README](README_OPENSOURCE.md) - Project overview
- [LICENSE](LICENSE) - MIT License
- [Issues](https://github.com/m98/fluent/issues) - Known issues
- [Discussions](https://github.com/m98/fluent/discussions) - Community forum

---

## 🎯 Priority Areas

We're especially interested in contributions for:

1. **Language-specific optimizations** - Grammar rules, common errors
2. **Audio features** - Pronunciation practice, listening exercises
3. **Visual enhancements** - Better progress charts, statistics
4. **Mobile support** - Companion app or mobile interface
5. **Performance** - Optimize data loading, improve speed
6. **Accessibility** - Make system more accessible
7. **Testing** - Add comprehensive test coverage

---

## ❓ Questions?

Don't hesitate to ask! Here's how:

1. Check existing [documentation](README_OPENSOURCE.md)
2. Search [past issues](https://github.com/m98/fluent/issues)
3. Ask in [discussions](https://github.com/m98/fluent/discussions)
4. Open a [new issue](https://github.com/m98/fluent/issues/new)

---

## 🙏 Thank You!

Every contribution makes this project better. Whether you're fixing a typo, reporting a bug, or adding a major feature - thank you for being part of this community!

**Happy Contributing!** 🚀

---

*Last updated: 2025-11-17*
