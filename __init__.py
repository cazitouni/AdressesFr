# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SimbleBan
                                 A QGIS plugin
 Recherche d'adresse
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-03-08
        copyright            : (C) 2022 by clément Zitouni
        email                : cazitouni@metrotopic.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SimbleBan class from file SimbleBan.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .simple_ban import SimbleBan
    return SimbleBan(iface)