"""
==========================================================
Face3D Studio AI

File:
material_exporter.py

Descrizione:
Esporta il file materiale Wavefront MTL.

Autore:
Marco Cantù

==========================================================
"""

from pathlib import Path


class MaterialExporter:
    """
    Esporta un file materiale MTL.
    """

    # ---------------------------------------------------------

    @staticmethod
    def export(
        obj_filename: str,
        texture_filename: str,
    ) -> Path:
        """
        Genera il file MTL associato all'OBJ.
        """

        obj_path = Path(obj_filename)

        mtl_path = obj_path.with_suffix(".mtl")

        texture_name = Path(texture_filename).name

        with mtl_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            file.write("# Face3D Studio AI\n")
            file.write("# Material\n\n")

            file.write("newmtl FaceMaterial\n")

            file.write("Ka 1.000 1.000 1.000\n")
            file.write("Kd 1.000 1.000 1.000\n")
            file.write("Ks 0.000 0.000 0.000\n")
            file.write("Ns 10.000\n\n")

            file.write(
                f"map_Kd {texture_name}\n"
            )

        return mtl_path