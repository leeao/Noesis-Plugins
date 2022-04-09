#PS Vita GXT Font texture Noesis plugin.
#by Allen


from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("PS Vita GXT Font texture",".gxt")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
    noesis.logPopup()
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readBytes(3)
        if idstring != b'GXT':
                return 0
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()
        idstring = bs.readInt() #GXT
        version = bs.readInt()
        numTex = bs.readInt()
        texDataOfs = bs.readInt()
        totalTexSize = bs.readInt()
        numP4Palettes = bs.readInt()
        numP8Palettes = bs.readInt()
        padding = bs.readInt()
        for i in range(numTex):
            offset = bs.readInt()
            dataSize = bs.readInt()
            paletteIndex = bs.readInt()
            texUnk = bs.readInt()
            texType = bs.readInt() #0x60 = linear
            texFormat = bs.readInt()
            width = bs.readShort()
            height = bs.readShort()
            mipmaps = bs.readShort()
            padding = bs.readShort()
            nextInfoOffset = bs.tell()
            bs.seek(offset)
            pixelBuffer = bs.readBytes(dataSize)
            if texFormat == 0x7000: #U8_R111
                texData = rapi.imageDecodeRaw(pixelBuffer,width,height,"A8")
                for p in range(len(texData)//4):
                    texData[p*4+0] = 255
                    texData[p*4+1] = 255
                    texData[p*4+2] = 255
                texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
                texList.append(texture)  
            bs.seek(nextInfoOffset)
    
        return 1
def texWriteRGBA(data, width, height, bs):

        bs.writeInt(0x545847)
        bs.writeInt(0x10000003)
        bs.writeInt(1)  #numTextures
        bs.writeInt(0x40)#tex Data Offset
        bs.writeInt(len(data)//4) #texture data size
        bs.writeInt(0)  #number P4 palettes
        bs.writeInt(1)  #number P8 palettes
        bs.writeInt(0)
        bs.writeInt(0x40)#first tex Data Offset
        bs.writeInt(len(data)//4) #texture data size
        bs.writeInt(-1)
        bs.writeInt(0)
        bs.writeInt(0x60000000) #tex type
        bs.writeInt(0x7000) #tex base format U8_R111
        bs.writeShort(width)
        bs.writeShort(height)
        bs.writeShort(1) #mipmaps
        bs.writeShort(0)  
        
        #write pixel
        for i in range(len(data)//4):
            bs.writeUByte(data[i*4+3])
            
        return 1