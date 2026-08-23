import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            StockPicksView()
                .tabItem {
                    Label("Picks", systemImage: "star.fill")
                }

            PortfolioPlaceholderView()
                .tabItem {
                    Label("Portfolio", systemImage: "chart.pie.fill")
                }
        }
    }
}

struct PortfolioPlaceholderView: View {
    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 64, height: 64)
                    .foregroundColor(.secondary)
                Text("Portfolio coming soon")
                    .font(.headline)
                Text("Track your holdings and performance here.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            .padding()
            .navigationTitle("Portfolio")
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
