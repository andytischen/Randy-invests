import SwiftUI

struct StockPicksView: View {
    @StateObject private var viewModel = StockPicksViewModel()
    @State private var showingAddSheet = false

    var body: some View {
        NavigationView {
            Group {
                if viewModel.picks.isEmpty {
                    emptyState
                } else {
                    picksList
                }
            }
            .navigationTitle("Stock Picks")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        showingAddSheet = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    EditButton()
                }
            }
            .sheet(isPresented: $showingAddSheet) {
                AddStockPickView(viewModel: viewModel)
            }
        }
    }

    private var picksList: some View {
        List {
            ForEach(viewModel.picks) { pick in
                StockPickRow(pick: pick)
            }
            .onDelete(perform: viewModel.delete)
            .onMove(perform: viewModel.move)
        }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "star.circle")
                .resizable()
                .scaledToFit()
                .frame(width: 64, height: 64)
                .foregroundColor(.secondary)
            Text("No Stock Picks Yet")
                .font(.headline)
            Text("Tap + to add your first pick.")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

struct StockPickRow: View {
    let pick: StockPick

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(pick.ticker)
                    .font(.headline)
                    .foregroundColor(.accentColor)
                Spacer()
                Text(pick.formattedTargetPrice)
                    .font(.headline)
                    .fontWeight(.semibold)
            }
            Text(pick.companyName)
                .font(.subheadline)
                .foregroundColor(.secondary)
            if !pick.notes.isEmpty {
                Text(pick.notes)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
        }
        .padding(.vertical, 4)
    }
}
