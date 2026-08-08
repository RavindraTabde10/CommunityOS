# Contributing to Riverdale Connect

Thank you for your interest in contributing to Riverdale Connect! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Commit Guidelines](#commit-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Testing Requirements](#testing-requirements)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Collaborate openly and transparently
- Maintain professional communication

---

## Getting Started

### Prerequisites

- **Backend**: Python 3.11+, PostgreSQL
- **Frontend**: Node.js 18+, npm/yarn
- **Tools**: Git, VS Code (recommended)

### Setup Development Environment

1. **Clone the repository:**
```bash
git clone <repository-url>
cd society_management_app
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

3. **Frontend setup:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your API endpoint
```

4. **Run the application:**
```bash
# Backend (in backend directory)
uvicorn app.main:app --reload

# Frontend (in frontend directory)
npm run dev
```

---

## Development Workflow

### Branch Strategy

```
main          # Production branch (protected)
  ↓
develop       # Integration branch (protected)
  ↓
feature/*     # Feature branches
bugfix/*      # Bug fix branches
hotfix/*      # Critical fix branches
release/*     # Release preparation branches
```

### Creating a New Feature

1. **Create a branch from develop:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

2. **Make your changes**

3. **Commit your changes:**
```bash
git add .
git commit -m "feat: add your feature description"
```

4. **Push to remote:**
```bash
git push origin feature/your-feature-name
```

5. **Create a Pull Request** to `develop` branch

---

## Coding Standards

### Backend (Python/FastAPI)

#### Style Guide
- Follow **PEP 8** guidelines
- Use **Black** for code formatting
- Use **type hints** for all functions
- Maximum line length: 100 characters

#### File Structure
```python
"""
Module docstring explaining purpose
"""

from typing import Optional
from fastapi import APIRouter, Depends

# Constants
MAX_ITEMS = 100

# Classes
class MyService:
    """Class docstring"""
    
    def __init__(self):
        pass
    
    def method_name(self, param: str) -> dict:
        """Method docstring"""
        pass

# Functions
def helper_function(arg: str) -> bool:
    """Function docstring"""
    pass
```

#### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

#### Documentation
- All public functions must have docstrings
- Use type hints
- Include parameter descriptions
- Specify return types

### Frontend (React/JavaScript)

#### Style Guide
- Use **ES6+** features
- Use **functional components** with hooks
- Use **Prettier** for formatting
- Maximum line length: 80 characters

#### Component Structure
```jsx
import React from 'react'
import { Box, Typography } from '@mui/material'
import PropTypes from 'prop-types'

/**
 * Component description
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Title text
 */
const MyComponent = ({ title, onAction }) => {
  // State
  const [state, setState] = React.useState(null)
  
  // Effects
  React.useEffect(() => {
    // Effect logic
  }, [])
  
  // Handlers
  const handleClick = () => {
    onAction()
  }
  
  // Render
  return (
    <Box>
      <Typography variant="h5">{title}</Typography>
    </Box>
  )
}

MyComponent.propTypes = {
  title: PropTypes.string.isRequired,
  onAction: PropTypes.func.isRequired,
}

export default MyComponent
```

#### Naming Conventions
- **Components**: `PascalCase.jsx`
- **Utilities**: `camelCase.js`
- **Hooks**: `useCamelCase.js`
- **Constants**: `UPPER_SNAKE_CASE`

---

## Commit Guidelines

### Conventional Commits

Use the following format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples
```bash
feat(auth): add JWT token refresh functionality

fix(issues): resolve photo upload error for large files

docs(api): update authentication endpoint documentation

refactor(services): simplify S3 upload logic

test(issues): add unit tests for issue creation
```

### Commit Message Rules
- Use present tense ("add" not "added")
- Use imperative mood ("move" not "moves")
- First line should be 50 characters or less
- Reference issues and PRs in footer

---

## Pull Request Process

### Before Creating PR

1. **Update from develop:**
```bash
git checkout develop
git pull origin develop
git checkout your-branch
git rebase develop
```

2. **Run tests:**
```bash
# Backend
pytest

# Frontend
npm test
```

3. **Check code quality:**
```bash
# Backend
black app/
flake8 app/

# Frontend
npm run lint
npm run format
```

### PR Requirements

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts with develop
- [ ] Descriptive PR title and description
- [ ] Linked to related issue(s)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code reviewed by self
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console errors
```

### Review Process

1. **Self-review** your code first
2. **Request review** from at least 1 team member
3. **Address feedback** promptly
4. **Resolve conflicts** if any
5. **Squash commits** before merge (if needed)

---

## Testing Requirements

### Backend Testing

**Unit Tests:**
```python
# tests/services/test_auth_service.py
import pytest
from app.services.auth_service import AuthService

def test_password_hashing():
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)
    assert AuthService.verify_password(password, hashed)
```

**API Tests:**
```python
# tests/api/test_issues.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_issue():
    response = client.post(
        "/api/v1/issues",
        json={"title": "Test Issue", "category": "electrical"}
    )
    assert response.status_code == 201
```

**Run tests:**
```bash
pytest --cov=app tests/
```

### Frontend Testing

**Component Tests:**
```javascript
// tests/components/IssueCard.test.jsx
import { render, screen } from '@testing-library/react'
import IssueCard from '../IssueCard'

test('renders issue title', () => {
  render(<IssueCard title="Test Issue" />)
  expect(screen.getByText('Test Issue')).toBeInTheDocument()
})
```

**Run tests:**
```bash
npm test
```

### Test Coverage Requirements

- **Backend**: Minimum 80% code coverage
- **Frontend**: Minimum 70% code coverage
- **Critical paths**: 100% coverage required

---

## Additional Guidelines

### API Changes

- Maintain backward compatibility
- Version breaking changes (v2, v3)
- Update API documentation
- Add migration guide if needed

### Database Changes

- Create Alembic migration
- Test migration up and down
- Document schema changes
- Provide seed data if needed

### Documentation

- Update README if needed
- Add inline comments for complex logic
- Update API documentation
- Create user guides for new features

### Security

- Never commit secrets or credentials
- Use environment variables
- Validate all user inputs
- Follow OWASP guidelines

---

## Questions or Issues?

- **Technical Questions**: Open a discussion on GitHub
- **Bug Reports**: Create an issue with bug template
- **Feature Requests**: Create an issue with feature template
- **Security Issues**: Email security@riverdaleconnect.com

---

## License

By contributing, you agree that your contributions will be licensed under the project's license.

Thank you for contributing to Riverdale Connect! 🎉
