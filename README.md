# Mini Task List - Django + HTMX

This is a small task list application built with Django and HTMX.

## Features

- List tasks.
- Add a new task inline.
- Toggle a task's "completed" status inline.
- Edit a task's title inline.
- Full functionality is maintained for users with JavaScript disabled.

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

Clone the repository and navigate into the project directory:

```bash
git clone git@github.com:spearw/mini-task-list.git
cd mini-task-list
```

Create and activate a virtual environment:

```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate
```
```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### Install Dependencies

Install requirements:

```bash
pip install -r requirements.txt
```

### Run Migrations

```bash
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

### Tests

```bash
python manage.py test
```

---

## Discussion
### Design Notes & Trade-offs

Due to the timeboxed nature of this project, several shortcuts were taken for simplicity.

- **Styling:** All CSS is done very minimally or inline. Styling in general needs attention. I considered using an out of the box CSS framework such as Tailwind, but standard css felt more appropriately transparent and simple.
- **Error Handling:** The application relies on Django's default error handling (e.g., 404 pages). More user-friendly error pages and specific handling for edge cases were not implemented.
- **Testing Scope:** The test suite relies exclusively on Django's server-side test client. While this is effective for verifying backend logic for both HTMX and non-JS POST requests, it cannot simulate a true browser environment. As a result, a bug where the non-JS interface was broken (due to a missing action attribute in forms) was not caught by the automated tests. A production-ready project should add a browser automation tool like Selenium or Playwright to the CI/CD pipeline to test the progressive enhancement features accurately.
- **Template Usage:** The \_task_table partial is not used in the edit_task_page.html template, as that page's <tbody> requires unique conditional logic to render the inline edit form. This should be cleaned up with inclusion tags.

Notes about HTMX boost vs hx- attributes.
I intentionally avoided using HTMX's hx-boost feature in favor of explicit attributes (hx-get, hx-target, hx-swap, etc.) on each interactive element. This decision was twofold:

- **Efficiency:** For this project's inline editing and adding features, sending small, targeted HTML partials from the server is significantly more efficient than the full-page <body> swaps that hx-boost performs.
- **Philosophy:** hx-boost is a tool designed to make a traditional Multi-Page Application (MPA) feel like a Single-Page Application (SPA). It simulates the "full page rerender" model that frameworks like React use, except the rendering happens on the server. A motivation for using HTMX is to avoid the significant architectural complexity and maintenance overhead common in SPAs (e.g., client-side routing, state management libraries, API layers). The approach of using targeted, partial updates more closely aligns with this goal, enhancing the simple server-rendered model instead of recreating an SPA architecture.

---

### Pros and Cons of HTMX (First Impressions)

#### Pros

- **Simplicity and Productivity:** HTMX is very productive. It allows for the creation of dynamic user interfaces without much overhead. The logic remains in the backend (Django views) and the presentation is controlled by simple HTML attributes.
- **Excellent for Progressive Enhancement:** HTMX is a natural fit for progressive enhancement. It was very simple to build standard HTML forms and links, and layer HTMX on top. Adding these features on top of Django felt very simple and natural.
- **Reduced Complexity:** HTMX avoids the need for a bloated frontend toolchain (no Node.js, webpack, etc.). It also eliminates the need to manage application state on the client, which is a major source of complexity in frontend frameworks. The server can be a single source of truth.
- **Efficiency:** For many use cases, sending small, pre-rendered HTML partials over the wire would be more efficient than sending a JSON payload that then requires client-side processing to be rendered into the DOM.
- **Long-term Maintainability:** The frontend JavaScript ecosystem cycles quickly. A React project from five years ago might require significant effort to update its build tools, state management libraries, and dependencies. Because HTMX has a very small, stable API and minimal dependencies, a Django+HTMX project is likely to be far easier to maintain and upgrade over the long term.

#### Cons

- **Not a Fit for Highly Interactive UIs:** HTMX does not feel like a replacement for frameworks like React or Vue when building highly stateful, complex applications like a dynamic graph database representation. For most use cases, it seems sufficient without the extra overhead.
- **Network Dependency:** Every user interaction requires a round-trip to the server. This makes HTMX unsuitable for applications that require significant offline functionality. However, most (in my experience) SPAs are built without this in mind, and are not very useful offline either.
- **Component Ecosystem:** React has a vast, mature ecosystem of third-party libraries and components. With HTMX, it feels as though you are more likely to have to build these components yourself given the need.

