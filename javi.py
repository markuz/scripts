#!/usr/bin/envp python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
#
# This file is part of my scripts project
#
# Copyright (c) 2014 Marco Antonio Islas Cruz
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2014 Marco Antonio Islas Cruz
# @license   http://www.gnu.org/licenses/gpl.txt
import os
import sys
import csv

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-r","--ruta", dest="ruta", 
        action="store", type="string",
        help="")

options, args = parser.parse_args()

if options.ruta:
    tmpfiles = os.listdir(options.ruta)
    files = [os.path.join(options.ruta, k) for k in tmpfiles]
else:
    files = args


def parse_file(path):
    """ Parse el archivo, devuelve un el nombre de la estacion
    y algunos datos en un diccionario.
    """

    with open (path,"rb") as f:
        lines= f.readlines()
    values  = {}
    if not lines:
        return values
    for index, line in enumerate(lines):
        if line.startswith("ESTACION"):
            items = [k.strip() for k in line.split() if k]
            values["codigo"] = items[1]
            latitud_index = items.index("LATITUD:")
            values["estacion"] = " ".join(items[2:latitud_index])
            latitud = items[latitud_index + 1]
            values["latitud_grados"] = latitud[:2]
            values["latitud_minutos"] = latitud[3:5]
            values["latitud_segundos"] = latitud[6:8]
            values["latitud_orientacion"] = items[5]

            longitud_index = items.index("LONGITUD:")
            longitud = items[longitud_index + 1]
            values["longitud_grados"] = "-"+longitud[:3]
            values["longitud_minutos"] = longitud[4:6]
            values["longitud_segundos"] = longitud[7:9]
            values["longitud_orientacion"] = items[8]
        elif line.startswith("TEMPERATURA MEDIA"):
            j = lines[index + 1].split()[1:]
            if j:
                values["temperatura"] = "%0.2f"%float(j[-1].replace(",",""))
        elif line.startswith("PRECIPITACION"):
            normal = lines[index + 1].split()[1:]
            if len(normal) > 1:
                values["precipitacion"] = "%0.2f"%float(normal[-1].replace(",",""))

            maxima = lines[index + 2].split()[2:]
            if len(maxima) > 1:
                values["precipitacion maxima"] = "%0.2f"%(sum([float(k.replace(",","")) for k in maxima if k])/12)
        elif line.startswith("EVAPORACIÓN TOTAL"):
            j = lines[index + 1].split()[1:]
            if len(j) > 1:
                values["evaporacion"] = "%0.2f"%float(j[-1].replace(",",""))
    return values

data = []
for archivo in files:
    tdata =  parse_file(archivo)
    if not tdata:
        print "Error procesando", archivo
        continue
    tmplist = []
    for key in ("codigo","estacion", "latitud_grados","latitud_minutos","latitud_segundos",
            "longitud_grados", "longitud_minutos","longitud_segundos","precipitacion",
            "precipitacion maxima", "temperatura","evaporacion"):
        tmplist.append(tdata.get(key, ""))
    data.append(tmplist)
writer = csv.writer(sys.stdout)
writer.writerows(data)
