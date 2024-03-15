class PDFExtractionCoordinator:
    def extract_data(self, pdf_file, option):
        if option == 'disciplinas_ministradas':
            strategy = DisciplinasMinistradasExtractionStrategy()
        elif option == 'todas_as_turmas':
            strategy = TodasAsTurmasExtractionStrategy()
        else:
            raise ValueError("Opção inválida")

        return strategy.extract_data(pdf_file)

class DisciplinasMinistradasExtractionStrategy:
    def extract_data(self, pdf_file):
        pass

class TodasAsTurmasExtractionStrategy:
    def extract_data(self, pdf_file):
        pass