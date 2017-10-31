# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pcbnew import *
import sys

def generate_outputs(fn, fab_output_path, preview_output_path):

    # Open the .kicad_pcb file
    board = LoadBoard(fn)

    # Set up the PLOT_CONTROLLER, which generates the gerber files
    plotter = PLOT_CONTROLLER(board)

    options = plotter.GetPlotOptions()
    options.SetOutputDirectory(fab_output_path)

    options.SetPlotFrameRef(False)
    options.SetPlotPadsOnSilkLayer(False)
    options.SetPlotValue(True)
    options.SetPlotReference(True)
    options.SetPlotInvisibleText(False)
    options.SetPlotViaOnMaskLayer(False)
    options.SetExcludeEdgeLayer(True);
    options.SetMirror(False)
    options.SetNegative(False)
    options.SetUseAuxOrigin(False)

    options.SetUseGerberProtelExtensions(True)
    options.SetUseGerberAttributes(False)
    options.SetSubtractMaskFromSilk(False)

    options.SetFormat(PLOT_FORMAT_GERBER)

    options.SetDrillMarksType(PCB_PLOT_PARAMS.NO_DRILL_SHAPE)
    options.SetScale(1)
    options.SetPlotMode(FILLED)
    options.SetLineWidth(FromMM(0.1))

    # Generate drill file
    drill = EXCELLON_WRITER(board)
    drill.SetFormat(False, EXCELLON_WRITER.DECIMAL_FORMAT)
    drill.CreateDrillandMapFilesSet(fab_output_path, True, False)

    # Plot everything needed for fabrication
    for file_suffix, layer, description in [
        ("F.Cu", F_Cu, "Top copper"),
        ("B.Cu", B_Cu, "Bottom copper"),
        ("F.Mask", F_Mask, "Top solder mask"),
        ("B.Mask", B_Mask, "Bottom solder mask"),
        ("F.Paste", F_Paste, "Top paste"),
        ("B.Paste", B_Paste, "Bottom paste"),
        ("F.SilkS", F_SilkS, "Top silkscreen"),
        ("B.SilkS", B_SilkS, "Bottom silkscreen"),
        ("Edge.Cuts", Edge_Cuts, "Board edge"),
    ]:
        plotter.SetLayer(layer)
        plotter.OpenPlotfile(file_suffix, PLOT_FORMAT_GERBER, description)
        plotter.PlotLayer()

    # Human-viewable previews
    options.SetOutputDirectory(preview_output_path)
    for file_suffix, description, layers, mirrored in [
        [
            "F.Preview",
            "Front preview",
            [
                (F_Cu, RED),
                (F_SilkS, WHITE),
                (Edge_Cuts, YELLOW),
            ],
            False,
        ],
        [
            "B.Preview",
            "Back preview",
            [
                (B_Cu, GREEN),
                (B_SilkS, WHITE),
                (Edge_Cuts, YELLOW),
            ],
            True,
        ],
    ]:
        options.SetMirror(mirrored)
        plotter.OpenPlotfile(file_suffix, PLOT_FORMAT_SVG, description)
        plotter.SetColorMode(True)

        for layer, color in layers:
            options.SetColor(color)
            plotter.SetLayer(layer)
            plotter.PlotLayer()

    # And we're done!
    plotter.ClosePlot()

if __name__ == '__main__':
    generate_outputs(sys.argv[1], 'gerber_tmp', '.')
