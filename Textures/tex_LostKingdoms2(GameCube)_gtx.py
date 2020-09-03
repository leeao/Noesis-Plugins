
#Decode BigEndian DXT1 code https://github.com/Zheneq/Noesis-Plugins/blob/master/lib_zq_nintendo_tex.py

from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("Lost Kingdoms 2 (GameCube)", ".gtx")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)
    bs.seek(4)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "GTX1":
        return 0
    return 1
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)
    fileSize = bs.readInt()
    idstring = noeStrFromBytes(bs.readBytes(4))
    unk1 = bs.readByte()
    unkFlag = bs.readByte()
    texForamt = bs.readByte()
    unk2 = bs.readByte()
    width = bs.readShort()
    height = bs.readShort()
    dataSize = fileSize - 32
    bs.seek(0x20)
    if texForamt == 0xe:
        print("CMPR DXT1")
        pixel = bs.readBytes(dataSize)
        textureData = textureParser.cmpr(pixel,width,height)
        texture = NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32)
    else:
        print("Unkonwn:",texFormat)    
    texList.append(texture)
    return 1


NINTEX_CMPR   = 0x0E


class pixelParser:
    @staticmethod
    def rgb565(rawPixel):
        t = bytearray(4)
        t[0] = (((rawPixel >> 11) & 0x1F) * 0xFF // 0x1F)
        t[1] = (((rawPixel >> 5)  & 0x3F) * 0xFF // 0x3F)
        t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
        t[3] = 0xFF
        return t
class textureParser:
    @staticmethod
    def cmpr(buffer, width, height):
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
        return textureData

dataFormats = {
    # code: decoder, bpp, block width, block height, bSimple, palette len
    0x0E: ("cmpr",   textureParser.cmpr,    4, 8, 8, False, 0)
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
