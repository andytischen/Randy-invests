import SwiftUI

@main
struct RandyInvestsApp: App {
    @StateObject private var portfolioViewModel = PortfolioViewModel()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(portfolioViewModel)
        }
    }
}
