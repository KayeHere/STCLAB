import Foundation
import Vision
import CoreImage
import AppKit
// usage: seg <in.jpg> <out_mask.png>
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
guard let ci = CIImage(contentsOf: url, options: [.applyOrientationProperty: true]) else { fatalError("load") }
let req = VNGeneratePersonSegmentationRequest()
req.qualityLevel = .accurate
req.outputPixelFormat = kCVPixelFormatType_OneComponent8
let h = VNImageRequestHandler(ciImage: ci, options: [:])
try h.perform([req])
guard let mask = req.results?.first?.pixelBuffer else { fatalError("no mask") }
var m = CIImage(cvPixelBuffer: mask)
m = m.transformed(by: CGAffineTransform(scaleX: ci.extent.width / m.extent.width, y: ci.extent.height / m.extent.height))
let ctx = CIContext()
let cg = ctx.createCGImage(m, from: ci.extent, format: .L8, colorSpace: CGColorSpaceCreateDeviceGray())!
let rep = NSBitmapImageRep(cgImage: cg)
try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[2]))
print("ok", cg.width, cg.height)
