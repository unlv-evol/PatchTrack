# mkdocs Features Used in Getting Started Documentation

This reference shows the mkdocs markdown features utilized in the improved `getting_started.md`.

## Admonitions

The following admonition types are used:

### Info Box (Blue)
```markdown
!!! info "Python Version"
    Content here
```

### Warning Box (Red/Orange)
```markdown
!!! warning "Security Note"
    Content here
```

### Note Box (Purple/Blue)
```markdown
!!! note "Alternative: Automated Script"
    Content here
```

### Success Box (Green)
```markdown
!!! success "Installation Complete!"
    Content here
```

## Tabs

Multi-platform setup using tabs:

```markdown
=== "macOS & Linux"

    ```bash
    command here
    ```

=== "Windows"

    ```powershell
    command here
    ```
```

## Collapsible Sections

Directory structure in a collapsible detail element:

```markdown
<details>
<summary><b>Click to expand directory structure</b></summary>

```
tree structure here
```

</details>
```

## Code Highlighting

Language-specified code blocks:

```bash
bash commands
```

```python
Python code
```

```json
JSON data
```

```powershell
PowerShell commands
```

## Markdown Tables

Command reference table:

```markdown
| Command | Description | Default |
|---------|-------------|---------|
| `-h` | Help | - |
```

## Links & References

Internal documentation links:

```markdown
[Reference Documentation](../reference/common.md)
```

## Horizontal Rules

Section separators:

```markdown
---
```

## Emoji Support

The mkdocs configuration enables emoji:

```markdown
📖 See the documentation
🐛 Report issues
💬 Get help
```

## Configuration Required in mkdocs.yml

The following extensions must be enabled (already configured):

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight
  - pymdownx.emoji
  - attr_list
  - def_list
  - pymdownx.tabbed:
      alternate_style: true
```

## Browser Compatibility

All features used are compatible with:
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers
- Dark mode support (configured in mkdocs.yml)

## Rendering

These features will render beautifully in:
- mkdocs with Material theme
- GitHub (markdown preview)
- Most markdown renderers

## Tips for Editing

1. **Admonitions**: Use `!!!` followed by type (info, warning, note, success)
2. **Tabs**: Use `===` with quoted title
3. **Details**: Use standard HTML `<details>` tags
4. **Code blocks**: Always specify language for syntax highlighting
5. **Tables**: Use pipes `|` for columns, hyphens for separator row
6. **Emoji**: Use standard emoji or markdown emoji syntax

## Resources

- [mkdocs Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [pymdownx Extensions](https://facelessuser.github.io/pymdown-extensions/)
- [Getting Started with mkdocs](https://www.mkdocs.org/)
