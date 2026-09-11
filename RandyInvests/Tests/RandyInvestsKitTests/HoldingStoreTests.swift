import XCTest
@testable import RandyInvestsKit

final class HoldingStoreTests: XCTestCase {
    private var suiteName: String!
    private var defaults: UserDefaults!

    override func setUp() {
        super.setUp()
        suiteName = "RandyInvestsKitTests.\(UUID().uuidString)"
        defaults = UserDefaults(suiteName: suiteName)
    }

    override func tearDown() {
        defaults.removePersistentDomain(forName: suiteName)
        defaults = nil
        super.tearDown()
    }

    func testLoadWithNothingSavedIsEmpty() {
        let store = UserDefaultsHoldingStore(defaults: defaults)
        XCTAssertTrue(store.load().isEmpty)
    }

    func testSaveThenLoadRoundTrips() {
        let store = UserDefaultsHoldingStore(defaults: defaults)
        let holdings = [
            Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 175),
            Holding(symbol: "MSFT", name: "Microsoft", shares: 2.5, averageCostBasis: 300, currentPrice: 350)
        ]
        store.save(holdings)
        XCTAssertEqual(UserDefaultsHoldingStore(defaults: defaults).load(), holdings)
    }

    func testCorruptDataLoadsAsEmpty() {
        defaults.set(Data("not json".utf8), forKey: UserDefaultsHoldingStore.defaultKey)
        XCTAssertTrue(UserDefaultsHoldingStore(defaults: defaults).load().isEmpty)
    }

    func testInMemoryStoreRoundTrips() {
        let store = InMemoryHoldingStore()
        let holdings = [Holding(symbol: "V", name: "Visa", shares: 1, averageCostBasis: 200, currentPrice: 250)]
        store.save(holdings)
        XCTAssertEqual(store.load(), holdings)
    }
}
