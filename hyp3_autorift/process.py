#!/usr/bin/env python3
"""
Package for processing with autoRIFT ICSE
"""

import argparse
import logging
import os

from hyp3lib.execute import execute
from hyp3lib.file_subroutines import mkdir_p
from isce.components.contrib.geo_autoRIFT import testGeogrid_ISCE
from isce.components.contrib.geo_autoRIFT import testautoRIFT_ISCE
from osgeo import gdal

from hyp3_autorift import io
from hyp3_autorift import geometry

log = logging.getLogger(__name__)


def process(master, slave, download=False, polarization='hh', orbits=None, aux=None, process_dir=None):
    """Process a Sentinel-1 image pair

    Args:
        master: Path to master Sentinel-1 SAFE zip archive
        slave: Path to slave Sentinel-1 SAFE zip archive
        download: If True, try and download the granules from ASF to the
            current working directory (default: False)
        orbits: Path to the orbital files, otherwise, fetch them from ASF
            (default: None)
        aux: Path to the auxiliary orbital files, otherwise, fetch them from ASF
            (default: None)
        process_dir: Path to a directory for processing inside
            (default: None; use current working directory)
    """
    
    # Ensure we have absolute paths
    master = os.path.abspath(master)
    slave = os.path.abspath(slave)

    if not os.path.isfile(master) or not os.path.isfile(slave) and download:
        log.info('Downloading Sentinel-1 image pair')
        dl_file_list = 'download_list.csv'
        with open('download_list.csv', 'w') as f:
            f.write(f'{os.path.basename(master)}\n'
                    f'{os.path.basename(slave)}\n')

        execute(f'get_asf.py {dl_file_list}')
        os.rmdir('download')  # Really, get_asf.py should do this...

    # TODO: Fetch orbit and aux files

    lat_limits, lon_limits = geometry.bounding_box(
        master, slave, orbits=orbits, aux=aux, polarization=polarization
    )
    
    # FIXME: Should integrate this functionality into hyp3lib.get_dem
    dem = geometry.find_jpl_dem(lat_limits, lon_limits, download=download)

    if process_dir:
        mkdir_p(process_dir)
        os.chdir(process_dir)

    io.format_tops_xml(master, slave, polarization, dem, orbits, aux)

    cmd = '${ISCE_HOME}/applications/topsApp.py topsApp.xml --end=mergebursts'
    execute(cmd, logfile='topsApp.txt', uselogging=True)

    m_slc = os.path.join(os.getcwd(), 'merged', 'master.slc.full')
    s_slc = os.path.join(os.getcwd(), 'merged', 'slave.slc.full')

    # FIXME: everything below is entirely silly.
    for slc in [m_slc, s_slc]:
        cmd = f'gdal_translate -of ENVI {slc}.vrt {slc}'
        execute(cmd, logfile='createImages.txt', uselogging=True)

    dhdx = dem.replace('_h.tif', '_dhdx.tif')
    dhdy = dem.replace('_h.tif', '_dhdy.tif')
    vx = dem.replace('_h.tif', '_vx.tif')
    vy = dem.replace('_h.tif', '_vy.tif')

    cmd = f'${{ISCE_HOME}}/components/contrib/geo_autoRIFT/testGeogrid_ISCE.py ' \
          f'-m {m_slc} -s {s_slc} -d {dem} -sx {dhdx} -sy {dhdy} -vx {vx} -vy {vy}'
    execute(cmd, logfile='testGeogrid.txt', uselogging=True)

    cmd = f'${{ISCE_HOME}}/components/contrib/geo_autoRIFT/testautoRIFT_ISCE.py ' \
          f'-m {m_slc} -s {s_slc} -g window_location.tif -o window_offset.tif ' \
          f'-vx window_rdr_off2vel_x_vec.tif -vy window_rdr_off2vel_y_vec.tif  -nc S'
    execute(cmd, logfile='testautoRIFT.txt', uselogging=True)






def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__,
    )
    parser.add_argument('master', type=os.path.abspath,
                        help='Master Sentinel-1 SAFE zip archive')
    parser.add_argument('slave', type=os.path.abspath,
                        help='Slave Sentinel-1 SAFE zip archive')
    args = parser.parse_args()

    process(args.master, args.slave)


if __name__ == "__main__":
    main()
