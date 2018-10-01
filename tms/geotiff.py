from datetime import datetime
from math import (
    cos,
    log,
    pi,
    radians,
    tan,
    trunc,
)
import os
from osgeo import (
    gdal,
    osr,
)
from PIL import Image
from shutil import rmtree
import sqlite3
import subprocess
import sys
from time import (
    gmtime,
    strftime
)
import warnings


input_path = 'TIF_FILES/'
output_path = 'static/img/maps/'


class TifInfo(object):
    def __init__(self, filename):
        # get the existing coordinate system
        self.ds = gdal.Open(input_path + filename)
        old_cs = osr.SpatialReference()
        old_cs.ImportFromWkt(self.ds.GetProjectionRef())

        # create the new coordinate system
        wgs84_wkt = """
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.01745329251994328,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4326"]]"""
        new_cs = osr.SpatialReference()
        new_cs.ImportFromWkt(wgs84_wkt)

        # create a transform object to convert between coordinate systems
        self.transform = osr.CoordinateTransformation(old_cs, new_cs)

        # get the point to transform, pixel (0,0) in this case
        width = self.ds.RasterXSize
        height = self.ds.RasterYSize
        gt = self.ds.GetGeoTransform()

        self.minx = gt[0]
        self.miny = gt[3] + width * gt[4] + height * gt[5]
        self.maxx = gt[0] + width * gt[1] + height * gt[2]
        self.maxy = gt[3]

    def get_lat_long(self):
        latlong = self.transform.TransformPoint(self.minx, self.miny)
        latlong += self.transform.TransformPoint(self.maxx, self.maxy)
        return latlong

    def get_center(self):
        latlong = self.get_lat_long()
        centerx = (latlong[0] + latlong[3]) / 2
        centery = (latlong[1] + latlong[4]) / 2
        return (centerx, centery)

    def get_created(self):
        created = self.ds.GetMetadataItem("TIFFTAG_DATETIME")
        if created:
            created = datetime.strptime(created, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        return created


class Marker(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.basename = os.path.splitext(self.filename)[0]
        self.extension = os.path.splitext(self.filename)[1]
        self.lng, self.lat = TifInfo(filepath).get_center()

    def zoomPointTotileXY(self, zoom):
        MinLatitude = -85.05112878
        MaxLatitude = 85.05112878
        MinLongitude = -180
        MaxLongitude = 180
        mapSize = (2 ** zoom) * 256

        latitude = min(max(self.lat, MinLatitude), MaxLatitude)
        longitude = min(max(self.lng, MinLongitude), MaxLongitude)
        p = {
            'x': (longitude + 180.0) / 360.0 * (1 << zoom),
            'y': (1.0 - log(tan(latitude * pi / 180.0) + 1.0 / cos(radians(self.lat))) / pi) / 2.0 * (1 << zoom)
        }

        tileX  = int(trunc(p['x']))
        tileY  = int(trunc(p['y']))
        x_point = int((p['x'] - tileX) * 256)
        y_point = int((p['y'] - tileY) * 256)
        return x_point, y_point

    def zoomPointToWMTS(self, zoom):
        lat_rad = radians(self.lat)
        n = 2.0 ** zoom
        x_tile = int((self.lng + 180.0) / 360.0 * n)
        y_tile = int((1.0 - log(tan(lat_rad) + (1 / cos(lat_rad))) / pi) / 2.0 * n)
        return x_tile, y_tile

    def save_tiles_at_zoom(self, zoom, output_path='./'):
        tile_width, tile_height = (256, 256)
        overlay = Marker(self.filepath)
        x_point, y_point = overlay.zoomPointTotileXY(zoom)
        x_tile, y_tile = overlay.zoomPointToWMTS(zoom)
        marker = Image.open("static/img/marker.png")
        marker_width, marker_height = marker.size

        tile = Image.new("RGBA", (tile_width * 3, tile_height * 3), (0, 0, 0, 0))
        tile.paste(marker, (tile_width + x_point - int(marker_width / 2), tile_height + y_point - marker_height))
        for i, num_i in enumerate((-1, 0, 1)):
            for j, num_j in enumerate((-1, 0, 1)):
                new_tile = tile.crop((
                    tile_width * i, tile_height * j, tile_width + tile_width * i, tile_height + tile_height * j
                ))
                if new_tile.getbbox():  # If the image is not full transparent
                    filename = output_path + '/' + str(overlay.basename) + '_markers/' + str(zoom) + '/' + \
                               str(x_tile + num_i) + '/' + str(y_tile + num_j) + '.png'
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    new_tile.save(filename, format="png")
        return True

    def save_tiles_to_zoom(self, zoom, output_path='./'):
        try:
            for i in range(zoom + 1):
                self.save_tiles_at_zoom(i, output_path)
        except Exception as e:
            print('\x1b[1;31;38m' + 'The marker tiles of the ' + str(self.basename + self.extension) +
                  ' file cannot be saved.' + '\x1b[0m')
            print('\x1b[1;31;38m' + 'Error: ' + e + '\x1b[0m')
        finally:
            print('The marker tiles for the ' + str(self.basename + self.extension) + ' file have been saved.')
        return True


class TifToDb(object):
    def __init__(self):
        self.con = sqlite3.connect('tms.sqlite3')

    def __del__(self):
        if self.con:
            self.con.close()

    def db_record_save(self, filename):
        self.mapname = os.path.splitext(filename)[0]
        self.extension = os.path.splitext(filename)[1]
        self.created = TifInfo(filename).get_created()
        latlong = TifInfo(filename).get_lat_long()
        self.minx = latlong[0]
        self.miny = latlong[1]
        self.maxx = latlong[3]
        self.maxy = latlong[4]
        center = TifInfo(filename).get_center()
        self.centerx = center[0]
        self.centery = center[1]

        with self.con:
            cur = self.con.cursor()
            publish = strftime("%Y-%m-%d %H:%M:%S", gmtime())

            try:
                cur.execute('''
                    INSERT INTO tiffmaps_overlay(mapname, extension, created, publish,
                                                 minx, miny, maxx, maxy, centerx, centery)
                    VALUES (:mapname, :extension, :created, :publish, :minx, :miny, :maxx, :maxy,
                            :centerx, :centery)''',
                    {
                        'mapname': self.mapname,
                        'extension': self.extension,
                        'created': self.created,
                        'publish': publish,
                        'minx': self.minx,
                        'miny': self.miny,
                        'maxx': self.maxx,
                        'maxy': self.maxy,
                        'centerx': self.centerx,
                        'centery': self.centery
                    }
                )
            except sqlite3.IntegrityError:
                updated = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                cur.execute('''
                    UPDATE tiffmaps_overlay SET extension=:extension, created=:created, updated=:updated,
                                                minx=:minx, miny=:miny, maxx=:maxx, maxy=:maxy, centerx=:centerx,
                                                centery=:centery WHERE mapname=:mapname''',
                    {
                        'mapname': self.mapname,
                        'extension': self.extension,
                        'created': self.created,
                        'updated': updated,
                        'minx': self.minx,
                        'miny': self.miny,
                        'maxx': self.maxx,
                        'maxy': self.maxy,
                        'centerx': self.centerx,
                        'centery': self.centery
                    }
                )
        return True

    def db_record_remove(self, filename):
        self.mapname = os.path.splitext(filename)[0]
        with self.con:
            cur = self.con.cursor()
            cur.execute('''SELECT * FROM tiffmaps_overlay WHERE mapname = ? ''', (self.mapname,))
            if not cur.fetchone():
                print('\x1b[1;31;38m' + 'The ' + filename + ' file does not exist in the database.' + '\x1b[0m')
                return False
            cur.execute('''DELETE FROM tiffmaps_overlay WHERE mapname = ? ''', (self.mapname,))
        return True

    def db_select_overlays(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute('''SELECT mapname, extension FROM tiffmaps_overlay''')
            return cur.fetchall()


class TifToJPG(object):
    def img_save(self, input_path, output_path, filename):
        mapname = os.path.splitext(filename)[0]

        try:
            warnings.simplefilter('ignore', Image.DecompressionBombWarning)
            img = Image.open(input_path + filename)
            if img.format is not 'TIFF':
                print('\x1b[1;31;38m' + 'The image is not in TIFF format.' + '\x1b[0m')
                return False
        except IOError:
            print('\x1b[1;31;38m' + 'The file cannot be found, or the image cannot be opened and identified.'
                  + '\x1b[0m')
            return False

        try:
            basewidth = 560
            print('The ' + mapname + ' file write operation in progress. Please wait.')
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(output_path + mapname + '/' + mapname + '.jpg', optimize=True)
            img.close()
        except Exception:
            print('\x1b[1;31;38m' + 'Preview of the ' + filename + ' file cannot be saved.' + '\x1b[0m')
        finally:
            print('\x1b[1;32;38m' + 'Preview of the ' + filename + ' file has been saved.' + '\x1b[0m')
        return True


class TifToTiles(object):
    def img_save(self, input_path, output_path, filename):
        if not os.path.exists(input_path + filename):
            print('\x1b[1;31;38m' + 'The ' + filename + ' file does not exist in the ' +
                  input_path + ' directory.' + '\x1b[0m')
            return False
        mapname = os.path.splitext(filename)[0]

        print('\x1b[1;34;38m' + 'Processing the ' + filename + ' file in progress. Please wait.' + '\x1b[0m')
        cmd_gdal = "python3 gdal2tiles.py -p mercator -z 0-19 -w none %s%s %s" % (
            input_path, filename, output_path + mapname
        )
        p1 = subprocess.Popen(cmd_gdal, shell=True, stderr=subprocess.PIPE)
        while True:
            out = p1.stderr.read(1)
            if out == b'' and p1.poll() != None:
                break
            if out != '' and not p1.stderr:
                sys.stdout.write(out)
                sys.stdout.flush()

        cmd_sh = "./filename.sh %s" % output_path + mapname
        p2 = subprocess.Popen(cmd_sh, shell=True, stdout=subprocess.PIPE)
        output, err = p2.communicate()
        print(output)

        if err:
            print(err)
            print('\x1b[1;31;38m' + 'The ' + filename + ' file cannot be saved.' + '\x1b[0m')
            return False
        else:
            Marker(filename).save_tiles_to_zoom(6, output_path)
            TifToDb().db_record_save(filename)
            TifToJPG().img_save(input_path, output_path, filename)
        print('\x1b[1;32;38m' + 'The ' + filename + ' file has been saved.' + '\x1b[0m')
        return True

    def img_all_save(self, input_path, output_path):
        filenames = [x for x in os.listdir(input_path) if x.endswith(".tif") or x.endswith(".tiff")]
        for filename in filenames:
            self.img_save(input_path, output_path, filename)
        if filenames:
            print('\x1b[1;32;42m' + 'All files have been saved.' + '\x1b[0m')
        else:
            print('\x1b[1;31;38m' + 'No files available in directory.' + '\x1b[0m')
        return True

    def img_remove(self, input_path, output_path, filename):
        mapname = os.path.splitext(filename)[0]
        TifToDb().db_record_remove(filename)
        try:
            os.remove(input_path + filename)
        except OSError:
            pass

        try:
            rmtree(output_path + mapname, ignore_errors=False)
        except OSError:
            print('\x1b[1;31;38m' + 'The ' + output_path + mapname + ' directory does not exist.' + '\x1b[0m')

        try:
            rmtree(output_path + mapname + '_markers', ignore_errors=False)
        except OSError:
            print('\x1b[1;31;38m' + 'The ' + output_path + mapname + '_markers directory does not exist.' + '\x1b[0m')
            return False

        print('\x1b[1;32;38m' + 'The ' + filename + ' file has been removed.' + '\x1b[0m')
        return True

    def img_all_remove(self, input_path, output_path):
        overlays = TifToDb().db_select_overlays()
        for i in range(len(overlays)):
            self.img_remove(input_path, output_path, overlays[i][0] + overlays[i][1])
        print('\x1b[1;32;38m' + 'All files have been removed.' + '\x1b[0m')
        return True


if __name__ == '__main__':
    if len(sys.argv) == 2:
        param_1 = sys.argv[1]
        param_2 = None
    elif len(sys.argv) == 3:
        param_1 = sys.argv[1]
        param_2 = sys.argv[2]
    else:
        param_1 = None
        param_2 = None

    if param_1 == 'save' and param_2 is not None:
        TifToTiles().img_save(input_path, output_path, param_2)
    elif param_1 == 'saveall' and param_2 is None:
        TifToTiles().img_all_save(input_path, output_path)
    elif param_1 == 'remove' and param_2 is not None:
        TifToTiles().img_remove(input_path, output_path, param_2)
    elif param_1 == 'removeall' and param_2 is None:
        TifToTiles().img_all_remove(input_path, output_path)
    elif param_1 == 'manual' and param_2 is None:
        print("""
            \nGenerate tiles and create a record in the database of the mapname.tif file:
            \x1b[1;34;38mpython3 geotiff.py save mapname.tif\x1b[0m
            Generate tiles and create a records in the database of the all files from TIF_FILES/ directory:
            \x1b[1;34;38mpython3 geotiff.py saveall\x1b[0m
            Remove tiles and record in the database of the mapname.tif file:
            \x1b[1;34;38mpython3 geotiff.py remove mapname.tif\x1b[0m
            Remove tiles and records of all files from TIF_FILES/ directory:
            \x1b[1;34;38mpython3 geotiff.py removeall\x1b[0m
            Display the manual:
            \x1b[1;34;38mpython3 geotiff.py manual\x1b[0m\n
        """)
    else:
        print('\x1b[1;33;38m' + 'Wrong arguments. Type "python3 geotiff.py manual" to display the manual.' + '\x1b[0m')
