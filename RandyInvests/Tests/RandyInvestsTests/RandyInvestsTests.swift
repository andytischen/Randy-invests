import XCTest
@testable import RandyInvests

final class HoldingTests: XCTestCase {

    func testMarketValue() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.marketValue, 2000, accuracy: 0.001)
    }

    func testTotalCost() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.totalCost, 1500, accuracy: 0.001)
    }

    func testGainLoss() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.gainLoss, 500, accuracy: 0.001)
    }

    func testGainLossPercent() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.gainLossPercent, 33.333, accuracy: 0.001)
    }

    func testGainLossPercentWithZeroCost() {
        let holding = Holding(symbol: "FREE", name: "Free Stock", shares: 10, averageCostBasis: 0, currentPrice: 100)
        XCTAssertEqual(holding.gainLossPercent, 0)
    }
}

final class PortfolioViewModelTests: XCTestCase {

    @MainActor func testAddNewHolding() {
        let vm = PortfolioViewModel()
        vm.holdings = []
        let holding = Holding(symbol: "MSFT", name: "Microsoft", shares: 5, averageCostBasis: 300, currentPrice: 350)
        vm.addHolding(holding)
        XCTAssertEqual(vm.holdings.count, 1)
        XCTAssertEqual(vm.holdings[0].symbol, "MSFT")
    }

    @MainActor func testAddDuplicateHoldingMerges() {
        let vm = PortfolioViewModel()
        vm.holdings = []
        let first = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 100, currentPrice: 150)
        let second = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 200, currentPrice: 160)
        vm.addHolding(first)
        vm.addHolding(second)
        XCTAssertEqual(vm.holdings.count, 1)
        XCTAssertEqual(vm.holdings[0].shares, 20, accuracy: 0.001)
        // Weighted average: (10*100 + 10*200) / 20 = 150
        XCTAssertEqual(vm.holdings[0].averageCostBasis, 150, accuracy: 0.001)
    }

    @MainActor func testRemoveHolding() {
        let vm = PortfolioViewModel()
        vm.holdings = [
            Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 175)
        ]
        vm.removeHoldings(at: IndexSet(integer: 0))
        XCTAssertTrue(vm.holdings.isEmpty)
    }

    @MainActor func testTotalMarketValue() {
        let vm = PortfolioViewModel()
        vm.holdings = [
            Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200),
            Holding(symbol: "MSFT", name: "Microsoft", shares: 5, averageCostBasis: 300, currentPrice: 400)
        ]
        // 10*200 + 5*400 = 2000 + 2000 = 4000
        XCTAssertEqual(vm.totalMarketValue, 4000, accuracy: 0.001)
    }

    @MainActor func testUpdatePrice() {
        let vm = PortfolioViewModel()
        vm.holdings = [
            Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 175)
        ]
        vm.updatePrice(for: "AAPL", newPrice: 200)
        XCTAssertEqual(vm.holdings[0].currentPrice, 200, accuracy: 0.001)
    }
}
