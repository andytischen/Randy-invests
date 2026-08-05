import SwiftUI

struct SearchView: View {
    @EnvironmentObject var viewModel: PortfolioViewModel
    @State private var query = ""
    @State private var results: [StockSearchResult] = []
    @State private var selectedResult: StockSearchResult?
    @State private var showingAddSheet = false

    /// Sample data simulating a search API response.
    private let sampleData: [StockSearchResult] = [
        StockSearchResult(symbol: "AAPL", name: "Apple Inc.", exchange: "NASDAQ"),
        StockSearchResult(symbol: "MSFT", name: "Microsoft Corporation", exchange: "NASDAQ"),
        StockSearchResult(symbol: "GOOGL", name: "Alphabet Inc.", exchange: "NASDAQ"),
        StockSearchResult(symbol: "AMZN", name: "Amazon.com Inc.", exchange: "NASDAQ"),
        StockSearchResult(symbol: "NVDA", name: "NVIDIA Corporation", exchange: "NASDAQ"),
        StockSearchResult(symbol: "TSLA", name: "Tesla Inc.", exchange: "NASDAQ"),
        StockSearchResult(symbol: "META", name: "Meta Platforms Inc.", exchange: "NASDAQ"),
        StockSearchResult(symbol: "BRK.B", name: "Berkshire Hathaway", exchange: "NYSE"),
        StockSearchResult(symbol: "JPM", name: "JPMorgan Chase & Co.", exchange: "NYSE"),
        StockSearchResult(symbol: "V", name: "Visa Inc.", exchange: "NYSE"),
        StockSearchResult(symbol: "UNH", name: "UnitedHealth Group", exchange: "NYSE"),
        StockSearchResult(symbol: "JNJ", name: "Johnson & Johnson", exchange: "NYSE"),
        StockSearchResult(symbol: "WMT", name: "Walmart Inc.", exchange: "NYSE"),
        StockSearchResult(symbol: "XOM", name: "Exxon Mobil Corporation", exchange: "NYSE"),
        StockSearchResult(symbol: "PG", name: "Procter & Gamble Co.", exchange: "NYSE")
    ]

    var filteredResults: [StockSearchResult] {
        guard !query.isEmpty else { return [] }
        let q = query.lowercased()
        return sampleData.filter {
            $0.symbol.lowercased().contains(q) || $0.name.lowercased().contains(q)
        }
    }

    var body: some View {
        NavigationStack {
            List(filteredResults) { result in
                Button {
                    selectedResult = result
                    showingAddSheet = true
                } label: {
                    SearchResultRow(result: result)
                }
                .buttonStyle(.plain)
            }
            .overlay {
                if query.isEmpty {
                    ContentUnavailableView(
                        "Search Stocks",
                        systemImage: "magnifyingglass",
                        description: Text("Type a symbol or company name to search.")
                    )
                } else if filteredResults.isEmpty {
                    ContentUnavailableView.search(text: query)
                }
            }
            .searchable(text: $query, prompt: "Symbol or company name")
            .navigationTitle("Search")
            .sheet(isPresented: $showingAddSheet) {
                if let result = selectedResult {
                    AddHoldingFromSearchView(searchResult: result)
                }
            }
        }
    }
}

private struct SearchResultRow: View {
    let result: StockSearchResult

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(result.symbol)
                    .font(.headline)
                Text(result.name)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            Text(result.exchange)
                .font(.caption2)
                .padding(.horizontal, 6)
                .padding(.vertical, 3)
                .background(.quaternary)
                .clipShape(RoundedRectangle(cornerRadius: 4))
        }
        .padding(.vertical, 2)
    }
}

#Preview {
    SearchView()
        .environmentObject(PortfolioViewModel())
}
