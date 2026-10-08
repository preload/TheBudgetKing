# The Budget King

> **A cross-platform personal transaction management application engineered to ingest, clean, track, and visualize financial data.**

---

## Core Architecture & Tech Stack

| Technology | Description |
| :--- | :--- |
| **Python** | Core application logic. |
| **Flet** | UI framework enabling single-codebase deployment across Desktop and Mobile. |
| **Pandas** | Data processing engine utilizing vectorized operations to handle large datasets efficiently. |
| **State Management** | Centralized state manager architecture decoupling UI components from data-processing logic. |

---

## Cross-Platform Deployment

* **Desktop:** Primary environment featuring a persistent top-level navigation bar for module access (Home, Import, Budget, Loans, Transactions).
* **Android:** Mobile-optimized build with a dedicated navigation bar layout. Includes an automated routine to clone bundled assets to writable internal app storage, bypassing platform read-only filesystem restrictions.

---

## Data Ingestion System

* **Multi-Source Parsing:** Extracts and cleans transaction data from raw PDF statements, CSV exports, and clipboard text.
* **Bulk File Import:** Paginated preview table with multi-row selection and batch control actions (`Upload all`, `Upload selected`, `Discard all`).
* **Manual Entry:** Dedicated modal interface for direct transaction injection requiring explicit parameters (Date, Authcode, Type, Merchant, Amount, Notes, Category).

---

## Transaction Management & Interface

* **Overview Module:** Paginated data table featuring merchant identification, auto-assigned vendor icons, currency values, notes, and categorical mapping. Pagination prevents UI thread blocking in the Flet client.
* **Record Mutation:** Modal dialog for updating existing transaction attributes (Date, Transaction ID, Merchant, Amount, Notes, Category).
* **Segmented Workflows:** Dedicated views for general ledger overview, duplicate record reconciliation, and filtered data export.
* **Search & Multi-Filter:** Column-specific string matching engine supporting concurrent stacked filter constraints.

---

## Screenshots

* TO BE ADDED

---

## Roadmap & Planned Implementations

* **Analytics Dashboard (Home View):** High-level financial reporting featuring cash-flow trends, merchant spend distributions, and category-level monthly comparisons.
* **Budgeting Engine:** Configurable expenditure caps per category, real-time threshold monitoring, and historical variance analysis.
* **Debt & Loan Tracking:** Amortization schedule calculations, interest versus principal breakdowns, and payoff projection modeling.
* **Multi-Account & User Profiles:** Local multi-user profile separation, encrypted storage, and isolated account ledgers.
* **Automated Categorization Rules:** Rule-based classification engine using regex matching to streamline raw statement parsing.
