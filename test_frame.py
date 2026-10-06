"""Draw a single 1920x1080 test frame and save it as test.png."""
import skia

WIDTH, HEIGHT = 1920, 1080

surface = skia.Surface(WIDTH, HEIGHT)
with surface as canvas:
    # Dark background
    canvas.clear(skia.Color(18, 20, 28))

    # Pale circle in the middle
    circle_paint = skia.Paint(AntiAlias=True, Color=skia.Color(232, 228, 214))
    canvas.drawCircle(WIDTH / 2, HEIGHT / 2 - 60, 260, circle_paint)

    # The word "hello", centred under the circle
    typeface = skia.FontMgr().matchFamilyStyle("Helvetica Neue", skia.FontStyle.Normal())
    font = skia.Font(typeface, 120)
    text_paint = skia.Paint(AntiAlias=True, Color=skia.Color(232, 228, 214))
    text = "hello"
    text_width = font.measureText(text)
    canvas.drawString(text, (WIDTH - text_width) / 2, HEIGHT / 2 + 340, font, text_paint)

surface.makeImageSnapshot().save("test.png", skia.kPNG)
print("Saved test.png")
