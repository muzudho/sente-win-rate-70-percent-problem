class XlUtils():


    @staticmethod
    def lookup_vertical(worksheet, column_letter_for_scan, find_value, column_letter_for_get, default_value=None):

        found_row_th = None
        for row_th in range(1, worksheet.max_row):

            if isinstance(find_value, list):
                is_found = worksheet[f'{column_letter_for_scan}{row_th}'].value in find_value

            else:
                is_found = worksheet[f'{column_letter_for_scan}{row_th}'].value == find_value


            if is_found:
                found_row_th = row_th
                break


        if found_row_th is None:
            return default_value


        return worksheet[f'{column_letter_for_get}{found_row_th}'].value
