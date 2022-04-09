from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Punisher xbox font raw", ".raw")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
    return 1

def noepyCheckType(data):
    return 1
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    width = 256
    height = 256
    palette = bs.readBytes(1024)
    pixel = bs.readBytes(width*height)
    pixel = rapi.imageFromMortonOrder(pixel,width,height,1)
    textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"b8g8r8p8") #BGRX888X 24bit
    
    #Im not test in game, if is BGRA8888 32bit just Remove "#"
    #textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"b8g8r8a8") #BGRA8888 32bit
    
    texList.append(NoeTexture("font", width, height, textureData, noesis.NOESISTEX_RGBA32))
    
    return 1

def texWriteRGBA(data, width, height, bs):
    if width != 256 and height != 256:
        print("Can't export. width and height not equal 256")        
        return 0
    imgPal = rapi.imageGetPalette(data, width, height, 256, 0, 1)
    idxPix = rapi.imageApplyPalette(data, width, height, imgPal, 256)
    for i in range(0,256):
        bs.writeUByte(imgPal[i*4+2])
        bs.writeUByte(imgPal[i*4+1])
        bs.writeUByte(imgPal[i*4+0])
        bs.writeUByte(imgPal[i*4+3]) 
    idxPix = rapi.imageToMortonOrder(idxPix,width,height,1)
    bs.writeBytes(idxPix)
    print("Export done!")
    return 1