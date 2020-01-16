# coding=utf-8

# Work-in-progress Nintendo texture library by Zhenёq
# https://github.com/Zheneq/Noesis-Plugins

# Acknowledgements:
# http://wiki.tockdom.com - format specs

from inc_noesis import *
import rapi

NINTEX_VERSION = 20180721

NINTEX_I4     = 0x00
NINTEX_I8     = 0x01
NINTEX_IA4    = 0x02
NINTEX_IA8    = 0x03
NINTEX_RGB565 = 0x04
NINTEX_RGB5A3 = 0x05
NINTEX_RGBA32 = 0x06
NINTEX_C4     = 0x08
NINTEX_C8     = 0x09
NINTEX_C14X2  = 0x0A
NINTEX_CMPR   = 0x0E


class pixelParser:
    @staticmethod
    def i4(rawPixel):
        t = bytearray(4)
        t[0] = rawPixel * 0x11
        t[1] = rawPixel * 0x11
        t[2] = rawPixel * 0x11
        t[3] = 0xFF
        return t

    @staticmethod
    def i8(rawPixel):
        t = bytearray(4)
        t[0] = rawPixel
        t[1] = rawPixel
        t[2] = rawPixel
        t[3] = 0xFF
        return t

    @staticmethod
    def ia4(rawPixel):
        t = bytearray(4)
        t[0] = (rawPixel & 0xF) * 0x11
        t[1] = (rawPixel & 0xF) * 0x11
        t[2] = (rawPixel & 0xF) * 0x11
        t[3] = (rawPixel >> 4) * 0x11
        return t

    @staticmethod
    def ia8(rawPixel):
        t = bytearray(4)
        t[0] = rawPixel & 0xFF
        t[1] = rawPixel & 0xFF
        t[2] = rawPixel & 0xFF
        t[3] = rawPixel >> 8
        return t

    @staticmethod
    def rgba32(rawPixel):
        t = bytearray(4)
        t[0] = (rawPixel >> 24) & 0xFF
        t[1] = (rawPixel >> 16) & 0xFF
        t[2] = (rawPixel >> 8)  & 0xFF
        t[3] = (rawPixel >> 0)  & 0xFF
        return t

    @staticmethod
    def rgb5a3(rawPixel):
        t = bytearray(4)
        if rawPixel & 0x8000 != 0:  # r5g5b5
            t[0] = (((rawPixel >> 10) & 0x1F) * 0xFF // 0x1F)
            t[1] = (((rawPixel >> 5)  & 0x1F) * 0xFF // 0x1F)
            t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
            t[3] = 0xFF
        else:  # r4g4b4a3
            t[0] = (((rawPixel >> 8)  & 0x0F) * 0xFF // 0x0F)
            t[1] = (((rawPixel >> 4)  & 0x0F) * 0xFF // 0x0F)
            t[2] = (((rawPixel >> 0)  & 0x0F) * 0xFF // 0x0F)
            t[3] = (((rawPixel >> 12) & 0x07) * 0xFF // 0x07)
        return t

    @staticmethod
    def rgb565(rawPixel):
        t = bytearray(4)
        t[0] = (((rawPixel >> 11) & 0x1F) * 0xFF // 0x1F)
        t[1] = (((rawPixel >> 5)  & 0x3F) * 0xFF // 0x3F)
        t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
        t[3] = 0xFF
        return t

    @staticmethod
    def ia8(rawPixel):
        t = bytearray(4)
        t[0] = rawPixel & 0xFF
        t[1] = t[0]
        t[2] = t[0]
        t[3] = (rawPixel >> 8) & 0xFF
        return t

    @staticmethod
    def to_rgb565(r, g, b, a = 0):
        r = r * 0x1f // 0xff & 0x1f
        g = g * 0x3f // 0xff & 0x3f
        b = b * 0x1f // 0xff & 0x1f
        return r << 11 + g << 5 + b


class textureParser:
    @staticmethod
    def cmpr(buffer, width, height, paletteBuffer=None, pixelFormat=None):
        df = NINTEX_CMPR
        name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[df]
        bs = NoeBitStream(buffer, NOE_BIGENDIAN)
        _width, _height = getStorageWH(width, height, df)
        textureData = bytearray(_width * _height * 4)

        for y in range(0, _height, bh):
            for x in range(0, _width, bw):
                for y2 in range(0, bh, 4):
                    for x2 in range(0, bw, 4):
                        c0 = bs.readUShort()
                        c1 = bs.readUShort()

                        c = [
                            pixelParser.rgb565(c0),
                            pixelParser.rgb565(c1),
                            bytearray(4),
                            bytearray(4)
                        ]

                        if c0 > c1:
                            for i in range(4):
                                c[2][i] = int((2 * c[0][i] + c[1][i]) / 3)
                                c[3][i] = int((2 * c[1][i] + c[0][i]) / 3)
                        else:
                            for i in range(4):
                                c[2][i] = int((c[0][i] + c[1][i]) * .5)
                                c[3][i] = 0

                        for y3 in range(4):
                            b = bs.readUByte()
                            for x3 in range(4):
                                idx = (((y + y2 + y3) * _width) + (x + x2 + x3)) * 4
                                textureData[idx : idx + 4] = c[(b >> (6 - (x3 * 2))) & 0x3]

        textureData = crop(textureData, _width, _height, 32, width, height)
        return NoeTexture("default", width, height, textureData, noesis.NOESISTEX_RGBA32)

    @staticmethod
    def rgba32(buffer, width, height, paletteBuffer=None, pixelFormat=None):
        df = NINTEX_RGBA32
        name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[df]
        _width, _height = getStorageWH(width, height, df)
        textureData = bytearray(_width * _height * 4)
        offset = 0

        for y in range(0, _height, bh):
            for x in range(0, _width, bw):
                for y2 in range(bh):
                    for x2 in range(bw):
                        idx = (((y + y2) * _width) + (x + x2)) * 4
                        textureData[idx + 0] = buffer[offset + 33]
                        textureData[idx + 1] = buffer[offset + 32]
                        textureData[idx + 2] = buffer[offset + 1]
                        textureData[idx + 3] = buffer[offset + 0]
                        offset += 2
                offset += 32

        textureData = crop(textureData, _width, _height, 32, width, height)
        return NoeTexture("default", width, height, textureData, noesis.NOESISTEX_RGBA32)

    @staticmethod
    def indexed(dataFormat, buffer, width, height, paletteBuffer, pixelFormat):
        name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[dataFormat]
        textureData = bytearray(width * height * 4)

        bs = NoeBitStream(paletteBuffer, NOE_BIGENDIAN)
        palette = [pixelFormats[pixelFormat](bs.readUShort()) for i in range(paletteLen)]

        tex = unswizzle(buffer, width, height, dataFormat)
        bs = NoeBitStream(tex, NOE_BIGENDIAN)

        if bpp == 16:
            for i in range(width * height):
                textureData[i * 4:(i + 1) * 4] = palette[bs.readUShort()]
        elif bpp == 8:
            for i in range(width * height):
                textureData[i * 4:(i + 1) * 4] = palette[bs.readUByte()]
        elif bpp == 4:
            for i in range(0, width * height, 2):
                b = bs.readUByte()
                textureData[i * 4:(i + 1) * 4] = palette[(b >> 4) & 0xf]
                textureData[(i + 1) * 4:(i + 2) * 4] = palette[b & 0xf]

        return NoeTexture("default", width, height, textureData, noesis.NOESISTEX_RGBA32)


    @staticmethod
    def c4(buffer, width, height, paletteBuffer, pixelFormat):
        return indexed(0x08, dataFormat, buffer, width, height, paletteBuffer, pixelFormat)

    @staticmethod
    def c8(buffer, width, height, paletteBuffer, pixelFormat):
        return indexed(0x09, dataFormat, buffer, width, height, paletteBuffer, pixelFormat)

    @staticmethod
    def c14x2(buffer, width, height, paletteBuffer, pixelFormat):
        return indexed(0x0A, dataFormat, buffer, width, height, paletteBuffer, pixelFormat)

dataFormats = {
    # code: decoder, bpp, block width, block height, bSimple, palette len
    0x00: ("i4",     pixelParser.i4,        4, 8, 8, True,  0),
    0x01: ("i8",     pixelParser.i8,        8, 8, 4, True,  0),
    0x02: ("ia4",    pixelParser.ia4,       8, 8, 4, True,  0),
    0x03: ("ia8",    pixelParser.ia8,      16, 4, 4, True,  0),
    0x04: ("rgb565", pixelParser.rgb565,   16, 4, 4, True,  0),
    0x05: ("rgb5a3", pixelParser.rgb5a3,   16, 4, 4, True,  0),
    0x06: ("rgba32", textureParser.rgba32, 32, 4, 4, False, 0),
    0x08: ("c4",     textureParser.c4,      4, 8, 8, False, 0x10),
    0x09: ("c8",     textureParser.c8,      8, 8, 4, False, 0x100),
    0x0A: ("c14x2",  textureParser.c14x2,  16, 4, 4, False, 0x400),
    0x0E: ("cmpr",   textureParser.cmpr,    4, 8, 8, False, 0)
}

pixelFormats = {
    0x00 : pixelParser.ia8,
    0x01 : pixelParser.rgb565,
    0x02 : pixelParser.rgb5a3
}


def crop(buffer, width, height, bpp, newWidth, newHeight):
    if width == newWidth and height == newHeight:
        return buffer

    res = bytearray(newWidth * newHeight * bpp // 8)

    lw = min(width, newWidth) * bpp // 8

    for y in range(0, min(height, newHeight)):
        dst = y * newWidth * bpp // 8
        src = y * width * bpp // 8
        res[dst: dst + lw] = buffer[src: src + lw]

    return res


def getStorageWH(width, height, df):
    name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[df]
    width  = (width  + bw - 1) // bw * bw
    height = (height + bh - 1) // bh * bh
    return width, height


def unswizzle(buffer, width, height, df):
    name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[df]
    stripSize = bpp * bw // 8

    _width, _height = getStorageWH(width, height, df)

    result = bytearray(_width * _height * bpp // 8)
    ptr = 0

    for y in range(0, _height, bh):
        for x in range(0, _width, bw):
            for y2 in range(bh):
                idx = (((y + y2) * _width) + x) * bpp // 8
                result[idx : idx+stripSize] = buffer[ptr : ptr+stripSize]
                ptr += stripSize

    return crop(result, _width, _height, bpp, width, height)


def swizzle(buffer, width, height, df):
    name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[df]
    stripSize = bpp * bw // 8

    _width, _height = getStorageWH(width, height, df)

    result = bytearray(_width * _height * bpp // 8)
    ptr = 0

    for y in range(0, _height, bh):
        for x in range(0, _width, bw):
            for y2 in range(bh):
                idx = (((y + y2) * width) + x ) * bpp // 8
                result[ptr : ptr+stripSize] = buffer[idx : idx+stripSize]
                ptr += stripSize

    return result


def convert(buffer, width, height, dataFormat, palette=None, pixelFormat=None):
    name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[dataFormat]

    if bSimple:
        tex = unswizzle(buffer, width, height, dataFormat)
        bs = NoeBitStream(tex, NOE_BIGENDIAN)
        textureData = bytearray(width * height * 4)

        if bpp == 32:
            for i in range(width * height):
                textureData[i*4:(i+1)*4] = decoder(bs.readUInt())
        elif bpp == 16:
            for i in range(width * height):
                textureData[i*4:(i+1)*4] = decoder(bs.readUShort())
        elif bpp == 8:
            for i in range(width * height):
                textureData[i*4:(i+1)*4] = decoder(bs.readUByte())
        elif bpp == 4:
            for i in range(0, width * height, 2):
                b = bs.readUByte()
                textureData[i*4:(i+1)*4] = decoder((b >> 4) & 0xf )
                textureData[(i+1)*4:(i+2)*4] = decoder(b & 0xf)

        return NoeTexture("default", width, height, textureData, noesis.NOESISTEX_RGBA32)

    else:
        return decoder(buffer, width, height, palette, pixelFormat)


def encode(buffer, width, height, dataFormat, palette=None, pixelFormat=None):
    if dataFormat != NINTEX_RGB565:
        raise ValueError("Data format not supported!")

    res = rapi.swapEndianArray(rapi.imageEncodeRaw(buffer, width, height, "b5g6r5"), 2)

    # res = NoeBitStream(bigEndian=NOE_BIGENDIAN)
    # for i in range(height * width):
    #     res.writeUShort(pixelParser.to_rgb565(buffer[4*i+0], buffer[4*i+1], buffer[4*i+2], buffer[4*i+3]))

    return swizzle(res, width, height, dataFormat)


def readTexture(bs, width, height, dataFormat, palette=None, pixelFormat=None):
    size = getTextureSizeInBytes(width, height, dataFormat)
    tex = bs.getBuffer(bs.tell(), bs.tell() + size)
    return convert(tex, width, height, dataFormat, palette, pixelFormat)


def writeTexture(buffer, width, height, dataFormat, palette=None, pixelFormat=None):
    return encode(buffer, width, height, dataFormat, palette, pixelFormat)


def getTextureSizeInBytes(width, height, dataFormat):
    name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[dataFormat]
    return bpp * ((width + bw - 1) // bw * bw) * ((height + bh - 1) // bh * bh) // 8


def getPaletteSizeInBytes(dataFormat, paletteLenOverride = 0):
    name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[dataFormat]
    if paletteLenOverride > 0:
        paletteLen = paletteLenOverride
    return paletteLen * 2  # palettes are always 16-bpp

    
def registerNoesisTypes():
    handle = noesis.register("Nintendo Texture Finder", ".nintex")
    noesis.setHandlerTypeCheck(handle, lambda x: 1)
    noesis.setHandlerLoadRGBA(handle, nintexLoadRGBA)
    return 1
    
    
def nintexLoadRGBA(data, texList):
    width = 256

    bs = NoeBitStream(data, NOE_BIGENDIAN)
    # newbs = NoeBitStream()
    # for i in range(bs.getSize() // 8):
    #     newbs.writeUInt64(bs.readUInt64())
    # bs = NoeBitStream(newbs.getBuffer(0x10, newbs.getSize()), NOE_BIGENDIAN)

    texList.append(NoeTexture("dxt1", width, (bs.getSize() // width) & 0xFFFFFFFC, bs.getBuffer(), noesis.NOESISTEX_DXT1))
    texList.append(NoeTexture("dxt3", width, (bs.getSize() // width) & 0xFFFFFFFC, bs.getBuffer(), noesis.NOESISTEX_DXT3))
    texList.append(NoeTexture("dxt5", width, (bs.getSize() // width) & 0xFFFFFFFC, bs.getBuffer(), noesis.NOESISTEX_DXT5))

    for dataFormat in dataFormats:
        name, decoder, bpp, bw, bh, bSimple, paletteLen = dataFormats[dataFormat]
        if paletteLen:
            continue
            
        height = ((bs.getSize() * 8) // (width * bpp)) & (~7)
        texList.append(readTexture(bs, width, height, dataFormat))
        texList[-1].name = name

    return len(texList)
