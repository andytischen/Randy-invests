# Randy Invests – iOS App

A SwiftUI investment portfolio tracker for iPhone and iPad.

## Features

- **Portfolio Overview** — See all your holdings at a glance with total market value and overall gain/loss.
- **Holding Detail** — Drill into any position to view cost basis, market value, and unrealised return.
- **Stock Search** — Browse and filter a list of stocks by symbol or company name and add them directly to your portfolio.
- **Add Holdings** — Manually enter shares, average cost basis, and current price for any position.
- **Merge Duplicate Positions** — Adding an existing symbol automatically calculates the weighted-average cost basis.
- **Persistent Storage** — Holdings are saved locally via `UserDefaults` and survive app restarts.

## Requirements

| Requirement | Version |
|---|---|
| Xcode | 15+ |
| iOS Deployment Target | 17.0+ |
| Swift | 5.9+ |

## Project Structure

```
RandyInvests/
├── Package.swift
├── Sources/
│   └── RandyInvests/
│       ├── RandyInvestsApp.swift        # App entry point
│       ├── Models/
│       │   ├── Holding.swift            # Holding data model
│       │   └── StockSearchResult.swift  # Search result model
│       ├── ViewModels/
│       │   └── PortfolioViewModel.swift # Observable portfolio state
│       └── Views/
│           ├── ContentView.swift              # Tab container
│           ├── PortfolioView.swift            # Portfolio list & summary
│           ├── HoldingRowView.swift           # Row in portfolio list
│           ├── HoldingDetailView.swift        # Holding detail screen
│           ├── AddHoldingView.swift           # Manual add holding form
│           ├── SearchView.swift               # Stock search screen
│           └── AddHoldingFromSearchView.swift # Add from search result
└── Tests/
    └── RandyInvestsTests/
        └── RandyInvestsTests.swift      # Unit tests
```

## Getting Started

1. Clone the repository.
2. Open `RandyInvests/` in Xcode 15 or later (File → Open… → select the `RandyInvests` folder).
3. Select an iOS Simulator or your iPhone as the run destination.
4. Press **⌘R** to build and run.

## Running Tests

Press **⌘U** in Xcode, or run from the terminal:

```bash
cd RandyInvests
swift test
```
