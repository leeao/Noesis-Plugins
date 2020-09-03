
from inc_noesis import *
'''
Select the edited DDS, PNG or any image that NOESIS supports to open.
Right click and select "export" convert to TEX format. Support parameter conversion.

Exporter usage:
By default, you do not need to enter any parameter and will export to DXT1 format.
-fmt 43 -mips    is export a texType 43 DXT5 have mipmaps.
-fmt 24          is export a texType 24 DXT5 no mipmaps.
-fmt 20          is export a texType 20 DXT1 no mipmaps.
-fmt 20 -mips    is export a texType 20 DXT1 have mipmaps.

'''

def registerNoesisTypes():
	handle = noesis.register("Mega Man Zero / ZX Legacy Collection PC textures", ".tex")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
	noesis.setHandlerWriteRGBA(handle, texWriteRGBA)

	noesis.addOption(handle, "-fmt", "export texture version <arg>,e.g. 20 24 43. 20 is DXT1,24 is DXT5,43 is DXT5 ",noesis.OPTFLAG_WANTARG)
	noesis.addOption(handle, "-mips", "auto create mipmaps", 0)
	noesis.logPopup()
	return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readBytes(4)
        if idstring != b'\x54\x45\x58\x00':
                return 0
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()
        idstring = bs.readInt()
        unk1 = bs.readShort() #0x00a2
        unk2 = bs.readShort() #0x2000
        info = bs.readUInt()
        mipmaps = info & 0xff
        width = (info & 0xFFF00) >> 6
        height = (info & 0xFFF00000) >> 19
        unk3 = bs.readByte() #0x1
        texType = bs.readByte() #0x14=DXT1 NOMIP 0x18=DXT5 NOMIP 0x2B=DXT5 MIP or NOMIP
        unk4 = bs.readByte() #0x1
        unk5 = bs.readByte() #0x0
        print(width,height)
        offsetTable = []        
        for i in range(mipmaps):
                offsetTable.append(bs.readUInt())
                bs.seek(4,1)
        dataSizeTable =[]
        for i in range(mipmaps):
                if i != (mipmaps-1):
                        dataSizeTable.append(offsetTable[i+1]-offsetTable[i])
                else:
                        dataSizeTable.append(bs.getSize()-offsetTable[i])
        bs.seek(offsetTable[0])
        pixelBuff = bs.readBytes(dataSizeTable[0])
        
        if texType == 0x14:
                texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT1)
        elif texType == 0x18:
                texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT5)
        elif texType == 0x2B:
                texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT5)           
        texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)
        
        return 1

#judge if it is a power of 2
def judge(num):
            num = int(num)
            return True if num == 0 or num & (num - 1) == 0 else False

def texWriteRGBA(data, width, height, bs):
        bs.writeInt(0x584554)
        bs.writeShort(0xa2)
        bs.writeShort(0x2000)        
        checkMip = True
        mipMaps = 1
        if (judge(width) == False) or (judge(height) == False):
                checkMip = False
                print("Can't export mipmaps,Please change the width and height to a power of 2.")
        texType = 20        
        if noesis.optWasInvoked("-mips") and checkMip ==  True:
                minWH = min(width,height)
                while(minWH != 1):
                        minWH //= 2
                        mipMaps += 1
        if noesis.optWasInvoked("-fmt"):
                fmt = int(noesis.optGetArg("-fmt"))
                if fmt == 24:
                        texType = 24
                elif fmt == 43:
                        texType = 43
                elif fmt == 20:
                        texType = 20

        tempMips = mipMaps & 0xFF
        tempWidth = (width << 6) & 0xFFF00
        tempHeight = (height << 19) & 0xFFF00000
        info = (tempMips | tempWidth | tempHeight) & 0xffffffff
        bs.writeInt(info)
        bs.writeByte(1)
        bs.writeByte(texType)
        bs.writeByte(1)
        bs.writeByte(0)

        for i in range(0, mipMaps):
                bs.writeInt(0)
                bs.writeInt(0)
        offsetTable = []

        for i in range(0, mipMaps):
                offsetTable.append(bs.tell())                
                mipW = max(width>>i, 1)
                mipH = max(height>>i, 1)
                mipPix = rapi.imageResample(data, width, height, mipW, mipH)
                if texType == 24:
                        print("geting DXT5 ...")
                        pixData = rapi.imageEncodeDXT(mipPix,4,mipW,mipH,noesis.NOE_ENCODEDXT_BC3)
                        print("geted DXT5")
                elif texType == 43:
                        print("geting DXT5...")
                        pixData = rapi.imageEncodeDXT(mipPix,4,mipW,mipH,noesis.NOE_ENCODEDXT_BC3)
                        print("geted DXT5")
                elif texType == 20:
                        print("geting DXT1...")
                        pixData = rapi.imageEncodeDXT(mipPix,4,mipW,mipH,noesis.NOE_ENCODEDXT_BC1)
                        print("geted DXT1")

                bs.writeBytes(pixData)

        bs.seek(16)
        for i in range(0, mipMaps):
                bs.writeInt(offsetTable[i])
                bs.writeInt(0)
        return 1
