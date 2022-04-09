#A Python Tile/Untile Library for XBOX360 textures.
#Thanks to Banz99 https://github.com/Banz99/Nier-Texture-Manager/blob/master/Decompressor/Form1.cs
#Thanks GTA XTD texture editor http://www.se7ensins.com/forums/topic/449976-release-gta-iv-xtd-editor/

def XGUntileSurfaceToLinearTexture(data, width, height, textureTypeStr):

    destData = bytearray(len(data))
    blockSize = 0
    texelPitch = 0

    if textureTypeStr == "DXT1":
        blockSize = 4
        texelPitch = 8
    elif textureTypeStr == "DXT5":
        blockSize = 4
        texelPitch = 16
    elif textureTypeStr == "UNC":
        blockSize = 2;
        texelPitch = 4;
    elif textureTypeStr == "CTX1":
        blockSize = 4;
        texelPitch = 8;
    else:
        print("Bad dxt type!")
        return 0

    blockWidth = width // blockSize
    blockHeight = height // blockSize

    for j in range(blockHeight):
        for i in range(blockWidth):
            blockOffset = j * blockWidth + i

            x = XGAddress2DTiledX(blockOffset, blockWidth, texelPitch)
            y = XGAddress2DTiledY(blockOffset, blockWidth, texelPitch)

            srcOffset = j * blockWidth * texelPitch + i * texelPitch
            destOffset = y * blockWidth * texelPitch + x * texelPitch
            if destOffset < len(data):             
                destData[destOffset:destOffset+texelPitch] = data[srcOffset:srcOffset+texelPitch]

    return destData

def XGTileSurfaceFromLinearTexture(data,width,height,textureTypeStr):
 
    destData = bytearray(len(data))
    blockSize = 0
    texelPitch = 0
    if textureTypeStr == "DXT1":
        blockSize = 4
        texelPitch = 8
    elif textureTypeStr == "DXT5":
        blockSize = 4
        texelPitch = 16
    elif textureTypeStr == "UNC":
        blockSize = 2;
        texelPitch = 4;
    elif textureTypeStr == "CTX1":
        blockSize = 4;
        texelPitch = 8;
    else:
        print("Bad dxt type!")
        return 0

    blockWidth = width // blockSize;
    blockHeight = height // blockSize;

    for j in range(blockHeight):
        for i in range(blockWidth):
            blockOffset = j * blockWidth + i

            x = XGAddress2DTiledX(blockOffset, blockWidth, texelPitch)
            y = XGAddress2DTiledY(blockOffset, blockWidth, texelPitch)

            destOffset = j * blockWidth * texelPitch + i * texelPitch
            srcOffset  = y * blockWidth * texelPitch + x * texelPitch
            if destOffset < len(data):                
                destData[destOffset:destOffset+texelPitch] = data[srcOffset:srcOffset+texelPitch]
    return destData
    
def XGAddress2DTiledX(Offset, Width, TexelPitch):

    AlignedWidth = (Width + 31) & ~31

    LogBpp = (TexelPitch >> 2) + ((TexelPitch >> 1) >> (TexelPitch >> 2))
    OffsetB = Offset << LogBpp
    OffsetT = ((OffsetB & ~4095) >> 3) + ((OffsetB & 1792) >> 2) + (OffsetB & 63)
    OffsetM = OffsetT >> (7 + LogBpp)

    MacroX = ((OffsetM % (AlignedWidth >> 5)) << 2)
    Tile = ((((OffsetT >> (5 + LogBpp)) & 2) + (OffsetB >> 6)) & 3)
    Macro = (MacroX + Tile) << 3
    Micro = ((((OffsetT >> 1) & ~15) + (OffsetT & 15)) & ((TexelPitch << 3) - 1)) >> LogBpp

    return (Macro + Micro)


def XGAddress2DTiledY(Offset,Width,TexelPitch):
    AlignedWidth = (Width + 31) & ~31

    LogBpp = (TexelPitch >> 2) + ((TexelPitch >> 1) >> (TexelPitch >> 2))
    OffsetB = Offset << LogBpp
    OffsetT = ((OffsetB & ~4095) >> 3) + ((OffsetB & 1792) >> 2) + (OffsetB & 63)
    OffsetM = OffsetT >> (7 + LogBpp)

    MacroY = ((OffsetM // (AlignedWidth >> 5)) << 2)
    Tile = ((OffsetT >> (6 + LogBpp)) & 1) + (((OffsetB & 2048) >> 10))
    Macro = (MacroY + Tile) << 3
    Micro = ((((OffsetT & (((TexelPitch << 6) - 1) & ~31)) + ((OffsetT & 15) << 1)) >> (3 + LogBpp)) & ~1)

    return (Macro + Micro + ((OffsetT & 16) >> 4))
