// swift-tools-version: 5.9
import PackageDescription

// RandyInvestsKit is the Foundation-only core of the app: the holding model,
// the portfolio arithmetic, persistence and locale-aware number parsing. It
// builds and tests on Linux. The SwiftUI app under App/ depends on it and is
// built with Xcode from the XcodeGen definition in project.yml.
let package = Package(
    name: "RandyInvests",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "RandyInvestsKit",
            targets: ["RandyInvestsKit"]
        )
    ],
    targets: [
        .target(
            name: "RandyInvestsKit",
            path: "Sources/RandyInvestsKit"
        ),
        .testTarget(
            name: "RandyInvestsKitTests",
            dependencies: ["RandyInvestsKit"],
            path: "Tests/RandyInvestsKitTests"
        )
    ]
)
