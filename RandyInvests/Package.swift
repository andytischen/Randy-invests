// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "RandyInvests",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "RandyInvests",
            targets: ["RandyInvests"]
        )
    ],
    targets: [
        .target(
            name: "RandyInvests",
            path: "Sources/RandyInvests"
        ),
        .testTarget(
            name: "RandyInvestsTests",
            dependencies: ["RandyInvests"],
            path: "Tests/RandyInvestsTests"
        )
    ]
)
