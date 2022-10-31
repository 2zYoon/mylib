BLACK_RGB   = (0, 0, 0)
WHITE_RGB   = (255, 255, 255)
RED_RGB     = (255, 0, 0)
GREEN_RGB   = (0, 255, 0)
BLUE_RGB    = (0, 0, 255)
YELLOW_RGB  = (255, 255, 0)
MAGENTA_RGB = (255, 0, 255)
CYAN_RGB    = (0, 255, 255)

# rgb_to_rgba: convert RGB 3-vector into RGBA 4-vector
#
#   @color: RGB 3-vector
#   @alpha: alpha (0-255)
#
#   @return: RGBA 4-vector (tuple)
def rgb_to_rgba(color, alpha):
    a = int(alpha)

    assert(len(color) == 3)
    assert(a <= 255 and a >= 0)

    return tuple(list(color) + [a])

# rgba_to_rgb: convert RGBA 4-vector into RGB 3-vector
#
#   @color: RGBA 4-vector
#
#   @return: RGB 3-vector
def rgba_to_rgb(color):
    assert(len(color) == 4)

    return tuple(color[:3])

# rgb_to_hex: convert RGB 3-vector into RGB hexcode
#
#  @color: RGB 3-vector
#
#  @return: RGB hexcode
def rgb_to_hex(color):
    assert(len(color) == 3)
    r, g, b = list(map(int, color))

    assert(r <= 255 and r >= 0)
    assert(g <= 255 and g >= 0)
    assert(b <= 255 and b >= 0)

    return r << 16 | g << 8 | b

# rgb_to_hex: convert RGBA 4-vector into RGBA hexcode
#
#  @color: RGBA 4-vector
#
#  @return: RGBA hexcode
def rgba_to_hex(color):
    assert(len(color) == 4)
    r, g, b, a = list(map(int, color))

    assert(r <= 255 and r >= 0)
    assert(g <= 255 and g >= 0)
    assert(b <= 255 and b >= 0)
    assert(a <= 255 and a >= 0)

    return r << 24 | g << 16 | b << 8 | a

# hex_to_rgb: convert RGB hexcode into RGB 3-vector
#
#   @hexcode: RGB hexcode
#
#   @return: RGB 3-vector
def hex_to_rgb(hexcode):
    assert(hexcode <= 0xffffff and hexcode >= 0)

    r = (hexcode & 0xff0000) >> 16
    g = (hexcode & 0xff00) >> 8
    b = (hexcode & 0xff) >> 0
    
    return (r, g, b)

# hex_to_rgba: convert RGBA hexcode into RGBA 4-vector
#
#   @hexcode: RGBA hexcode
#
#   @return: RGBA 4-vector
def hex_to_rgba(hexcode):
    assert(hexcode <= 0xffffffff and hexcode >= 0)

    r = (hexcode & 0xff000000) >> 24
    g = (hexcode & 0xff0000) >> 16
    b = (hexcode & 0xff00) >> 8
    a = (hexcode & 0xff) >> 0
    
    return (r, g, b, a)