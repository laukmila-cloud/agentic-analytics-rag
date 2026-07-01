class KPICalculator:
    def calculate_variation(
        self,
        current_value: float,
        previous_value: float,
    ) -> dict:
        if previous_value == 0:
            return {
                "success": False,
                "error": "No se puede calcular variación porcentual con valor anterior igual a cero.",
            }

        variation = ((current_value - previous_value) / previous_value) * 100

        return {
            "success": True,
            "current_value": current_value,
            "previous_value": previous_value,
            "variation_percentage": round(variation, 2),
            "interpretation": self._interpret_variation(variation),
        }

    def calculate_gap(
        self,
        value_a: float,
        value_b: float,
        label_a: str = "A",
        label_b: str = "B",
    ) -> dict:
        gap = value_a - value_b

        return {
            "success": True,
            "label_a": label_a,
            "value_a": value_a,
            "label_b": label_b,
            "value_b": value_b,
            "absolute_gap": round(gap, 2),
            "higher_value": label_a if value_a > value_b else label_b,
        }

    def _interpret_variation(self, variation: float) -> str:
        if variation > 0:
            return "El indicador aumentó frente al periodo anterior."
        if variation < 0:
            return "El indicador disminuyó frente al periodo anterior."
        return "El indicador se mantuvo estable frente al periodo anterior."