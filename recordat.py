from constants import evaDatabase
import re
import random
import sqlite3
from thefuzz import fuzz
import time
import datetime
import traceback

from for_the_record import Lectura
from evaIrene3 import Eva as E

def mes_a_numero(mes: str) -> int:
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'setiembre': 9, 'octubre': 10,
        'noviembre': 11, 'diciembre': 12}
    return meses.get(mes.lower(), 0)

def numero_a_mes(numero: int) -> str:
    numero = int(numero)
    meses = {1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'}
    return meses.get(numero, '')

def numero_a_diaSemana(numero: int) -> str:
    numero = int(numero)
    semana = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    return semana.get(numero, '')


class orios:
    def __init__(self, chat_id: int = None, vaina: str = None):
        self.meses = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
                      'agosto', 'septiembre', 'setiembre', 'octubre', 'noviembre', 'diciembre')
        self._usr = chat_id
        self._que = vaina

    def _get_db_connection(self):
        """Establece una conexión con la base de datos SQLite."""
        return sqlite3.connect(evaDatabase)

    def situacion(self):
        try:
            que = self._que
            
            if (que.split(' ')[0] == 'recordatorios' or E.verbos_magicos(que, 'pasar') or E.verbos_magicos(que, 'mostrar') or E.verbos_magicos(que, 'dar')) and not re.search('\d', que):
                return self.entregar()
            
            if E.verbos_magicos(que, 'buscar'):
                return self.buscar()
            
            if E.verbos_magicos(que, 'eliminar') or que.split(' ')[0] == 'eliminar':
                return self.lista_de_eliminar()
            
            return self.creacion()
        
        except Exception as e:
            return traceback.format_exc(), 404


    def entregar(self) -> tuple[str,int]:
        '''
        dar los recodatorios al urs.
        todos o los del mes si especificado
        '''
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar si self._que contiene un mes
                mes_especifico = self._find_nombre_mes(self._que)

                if mes_especifico:
                    # Filtrar recordatorios solo para el mes especificado
                    cursor.execute('''
                        SELECT dia, mes, texto FROM recordatorios
                        WHERE usr_id = ? AND mes = ? AND completo = 0
                        ORDER BY dia
                    ''', (self._usr, mes_a_numero(mes_especifico)))
                else:
                    # Obtener todos los recordatorios
                    cursor.execute('''
                        SELECT dia, mes, texto FROM recordatorios
                        WHERE usr_id = ? AND completo = 0
                        ORDER BY mes, dia
                    ''', (self._usr,))
                conn.commit()

                recordatorios = cursor.fetchall()

            if not recordatorios:
                return 'no hay recordatorios a tu nombre, si quieres crear uno pídemelo como:\n\n<i>recordatorio 14 de abril cumple pepito los palotes</i>', 0

            # Agrupar por mes y día
            agrupados = {}
            for dia, mes, texto in recordatorios:
                try:
                    mes = int(mes)
                except:
                    mes = mes_a_numero(mes)

                if mes not in agrupados:
                    agrupados[mes] = {}
                if dia not in agrupados[mes]:
                    agrupados[mes][dia] = []
                if texto == '':
                    texto = 'Null'
                agrupados[mes][dia].append(texto.capitalize())

            usr_today, usr_tomonth = self._get_today()
            total = []

            # decidir qué meses mostrar
            if mes_especifico:
                meses_a_mostrar = [int(mes_a_numero(mes_especifico))]
            else:
                meses_a_mostrar = sorted(agrupados)

            for mes in meses_a_mostrar:
                mes_t = numero_a_mes(mes).upper()

                saludito = ['<b>','</b>'] if mes == usr_tomonth else ['','']
                total.append(f'\n{saludito[0]}• {mes_t} •{saludito[1]}')

                for dia in sorted(agrupados.get(mes, {})):
                    textos_unidos = '\n\t\t\t\t\t\t\t\t'.join(agrupados[mes][dia])
                    total.append(f'{dia:02} - {textos_unidos}')

            return '\n'.join(total), 0

        except Exception as e:
            # return traceback.format_exc(), 0
            return f'error al obtener recordatorios: {e}', 0

    def buscar(self) -> tuple[str,int]:
        '''
        buscar un item en los recordatorios.
        devuelve las fechas con los textos
        '''
        item = self._identificar_item()
        si = []
        poco = []
        
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
        
            cursor.execute('''
                SELECT dia, mes, texto FROM recordatorios
                WHERE usr_id = ?
            ''', (self._usr,))
            conn.commit()

        
            for dia, mes, texto in cursor.fetchall():        
                if fuzz.ratio(item, texto) > 85:
                    si.append(f'<u>{texto.upper()}</u> el {dia} de {numero_a_mes(mes)}')
        
                elif fuzz.partial_ratio(item, texto) > 85:
                    poco.append(f'{dia}/{mes} - {texto}')
        
        if not si and not poco:
            return f'no encontré ningún recordatorio similar a <i>{item}</i>', 0
        
        respuesta = []
        if si:
            respuesta.append('• ' + '\n• '.join(si))
        if poco:
            respuesta.append(f'\ncoincidencias similares:\n' + '\n '.join(poco))
        
        return '\n'.join(respuesta), 0

    def lista_de_eliminar(self) -> tuple[tuple,int]:
        '''
        devuelve una lista con los recordatorios
        la lista es: [[texto, id], ...]
        :return: (dia, mes, lista), 666
        '''
        que = self._que

        if 'por id' in que:
            _id = int(que.split(' ')[-1])
            self.eliminar_por_ID(_id)
            return 'listo', 0
        
        dia, mes_t = self._find_fecha_compelta(que)

        if not dia:
            return f'dime bien de cual día', 0
        if not mes_t:
            return 'no pude reconocerte el mes', 0

        
        lista = self.lista_de_la_fecha(dia, mes_a_numero(mes_t))
        
        if not lista:
            return f'no tienes recordatorios el {dia} de {mes_t}', 0
        
        return (dia, mes_t, lista), 666

    def creacion(self) -> tuple[str,int]:
        '''
        crear el recodatorio
        '''
        que = self._que

        # buscamos el desface horario
        try:
            self.desface = Lectura(self._usr).dif_tics or 0
        except:
            self.desface = 0

        try:
            # si se indica el hoy o manana
            if que.split(' ')[que.split(' ').index('recordatorio') + 1] == 'hoy':
                dia = self._dia_seter(0, self.desface)
                mes = self._mes_seter(0, self.desface)
                # el item está después de "hoy"
                que = que.split('hoy')[1].strip()
            
            elif que.split(' ')[que.split(' ').index('recordatorio') + 1] == 'mañana':
                dia = self._dia_seter(1, self.desface)
                mes = self._mes_seter(1, self.desface)
                # el item está después de "mañana"
                que = que.split('mañana')[1].strip()
            
            # si no, buscamos la fecha
            else:
                try:
                    dia, mes_t = self._find_fecha_compelta(que)
                    
                    if not dia:
                        return f'un mes no puede tener {dia} días', 0
                    if not mes_t:
                        return 'no logro pillar el mes en tu mensaje', 0
                    
                    # el item está después del mes
                    que = que.split(mes_t)[1].strip()
                    
                    mes = mes_a_numero(mes_t)
                
                except:
                    # si nada de lo anterior funciona, buscamos por dia de la semana.
                    # esto lo hacemos despues de todo pq el recordatoio podria incluir un dia de la semana

                    dia, mes, que = self._obt_dia_semana()
                    if not dia:
                        return 'no entiendo la fecha :c', 404

            self._crear_recordatorio_en_el_SQL(dia, mes, que)

            mes_t = numero_a_mes(mes)

            import faltan # <---------- esto es ordinario
            nn = f'{dia} de {mes_t}'
            aun = faltan.tantosDias(nn)

            respuesta = random.choice([
                f'el {dia} de {mes_t} te recuerdo <i>{que}</i> ({aun})', 
                f'<i>{que}</i> el {dia} de {mes_t} ({aun})', 
                f'{dia}/{mes_t} - {que} ({aun})', 
                f'<i>{que}</i> guardado ({aun})',
                f'el {dia} de {mes} te avisaré de <i>{que}</i> ({aun})',
                ])
            return respuesta, 0
        
        except Exception as e:
            # return traceback.format_exc(), 404
            return 'algo falló en la redacción para agendar un nuevo recordatorio', 404


    def _ticks(self, extra: int) -> datetime:
        return datetime.datetime.fromtimestamp(time.time() + extra)

    def _dia_seter(self, dias_extra: int, desface: int = 0) -> int:
        '''
        se da el dia considerando cuanto falta y el desface del usuario
        '''
        dias_extra = int(dias_extra)
        return int(self._ticks(24 * dias_extra * 3600 + desface).strftime('%d'))

    def _mes_seter(self, dias_extra: int, desface: int = 0) -> int:
        '''
        se da el mes considerando cuanto falta y el desface del usuario
        '''
        dias_extra = int(dias_extra)
        return int(self._ticks(24 * dias_extra * 3600 + desface).strftime('%m'))

    def _obt_dia_semana(self) -> tuple[int, int, str]:
        try:
            p = Lectura(self._usr)
            now = datetime.datetime.fromtimestamp(time.time() + p.dif_tics).isoweekday()
            dias_semana = {
                'lunes': 1,
                'martes': 2,
                'miercoles': 3,
                'miércoles': 3,
                'jueves': 4,
                'viernes': 5,
                'sabado': 6,
                'sábado': 6,
                'domingo': 7}
        
            for d in dias_semana:
                if d in self._que:
                    numero_pedido = dias_semana[d]
                    diaSemana = d
                    break
            else:
                return False, 0, 0
            
            # numero de dias hasta la fecha
            numero_querido = numero_pedido - now
            if now >= numero_pedido:
                numero_querido += 7

            # obtenemos fecha 
            dia = self._dia_seter(numero_querido, self.desface)
            mes = self._mes_seter(numero_querido, self.desface)

            recordatorio = self._que.split(diaSemana)[1].strip()
            
            return dia, mes, recordatorio
        
        except:
            return False, 0, 0

    def _find_numero_dia(self, que: str) -> int:
        '''
        Busca el primer número de 1 o 2 dígitos, que será el día del mes.
        '''
        numeros = re.findall(r'\b\d{1,2}\b', que)  # busca números de 1 o 2 dígitos
        if numeros:
            dia = int(numeros[0])
            if 1 <= dia <= 31:
                return dia
        return None

    def _find_nombre_mes(self, que: str) -> str:
        '''
        busca el nombre del mes
        '''
        mes = None
        for ms in self.meses:
            if ms in que:
                mes = ms
                break
        return mes

    def _find_fecha_compelta(self, que: str) -> tuple[int,str]:
        return self._find_numero_dia(que), self._find_nombre_mes(que)

    def _identificar_item(self) -> str:
        """
        aqui se busca en el texto
        lo que se quiere buscar en el SQL
        """
        try:
            v = self._que.split(' ')
            if v.index('busca') < v.index('recordatorio'):
                cual = self._que.split('recordatorio')[1].strip()
            else:
                cual = self._que.split('busca')[1].strip()
        except:
            v = self._que.split(' ')
            if v.index('busca') < v.index('recordatorios'):
                cual = self._que.split('recordatorios')[1].strip()
            else:
                cual = self._que.split('busca')[1].strip()
        return cual

    def _get_today(self) -> tuple[int,int]:
        '''
        devuelve el dia y mes de hoy del ususario
        '''
        p = Lectura(self._usr)
        fecha_usuario = datetime.datetime.fromtimestamp(time.time() + p.dif_tics)
        mes = fecha_usuario.month
        dia = fecha_usuario.day
        return dia, mes

    def _crear_recordatorio_en_el_SQL(self, dia: int, mes: int, item: str) -> str:
        # porsiacaso
        try:
            int(mes)
        except:
            mes = mes_a_numero(mes)

        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO recordatorios (usr_id, dia, mes, texto, completo)
                    VALUES (?, ?, ?, ?, 0)
                ''', (self._usr, dia, mes, item))
                conn.commit()

            return f'recordatorio {item} del {dia} de {mes} creado'
        
        except Exception as e:
            return f'error al crear recordatorio: {e}'

    def _crear_tabla_enviados(self):
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recordatorios_enviados (
                id INTEGER,
                msg_id INTEGER)
                ''')
            conn.commit()
    

    def guardar_enviado(self, _id: int, msg_id: int) -> bool:
        '''
        para guardar los msg_id de los enviados
        '''
        self._crear_tabla_enviados()

        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recordatorios_enviados (id, msg_id)
                VALUES (?, ?)
            ''', (_id, msg_id))
            conn.commit()
        return True

    def lista_ids_enviados(self, _id: int) -> list:
        '''
        eso mismo.
        '''
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT msg_id FROM enviados
                WHERE id = ?
            ''', (_id,))
            resultados = cursor.fetchall()
            
        # Extraer solo los msg_id de las tuplas
        return [fila[0] for fila in resultados]    

    def eliminar_por_ID(self, _id: int) -> tuple[str,int]:
        '''
        eliminar el recordatorio por su id
        
        :param _id: id del recordatorio
        :return: el texto del recodatorio
        '''

        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                # extraemos el texto del recordatorio y revisamos si existe
                cursor.execute('''
                    SELECT texto FROM recordatorios
                    WHERE id = ?
                    ''', (_id,))
                conn.commit()           

                row = cursor.fetchone()

                if not row:
                    return 'no tenías ese recordatorio guardado', 404
                
                texto_recordatorio = row[0]
                
                # eliminarmos el recordatorios
                cursor.execute('''
                    DELETE FROM recordatorios
                    WHERE id = ?
                    ''', (_id,))
                conn.commit()           
            
            return texto_recordatorio, 0
        
        except Exception as e:
            return f'error al eliminar: {e}', 404

    def lista_de_la_fecha(self, dia: int, mes: int, completo: str = "%") -> list:
        '''
        se devuelven los recordatiors de la fecha especificada del usr,
        en forma de LISTA.
        Si no se define completo se buscan todos

        :paam compelto: 0 para incompeltos, 1 para compeltos, nada para todo
        '''
        try:
            dia = int(dia)  # Convertir dia y mes a entero porsiacaso
            mes = int(mes)

            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # en caso de que se indique completo o no
                if completo == "%":
                    cursor.execute('''
                        SELECT texto, id FROM recordatorios
                        WHERE usr_id = ? AND dia = ? AND mes = ?
                    ''', (self._usr, dia, mes))
                
                else:
                    cursor.execute('''
                        SELECT texto, id FROM recordatorios
                        WHERE usr_id = ? AND dia = ? AND mes = ? AND completo = ?
                    ''', (self._usr, dia, mes, int(completo)))
                
                conn.commit()           
                
                resultados = []
                for texto, id_ in cursor.fetchall():
                    if texto.strip():  # si no está vacío ni puras spaces
                        resultados.append((texto, id_))
                    else:
                        # guardar con un texto especial
                        resultados.append(("Null", id_))

                # resultados = [(row[0], row[1]) for row in cursor.fetchall()]
                
                return resultados if resultados else False
        
        except (sqlite3.Error, ValueError) as e:
            return traceback.format_exc()
    
    def de_la_fecha(self, dia: int, mes: int) -> str:
        '''
        se devuelven los recordatiors de la fecha especificada del usr,
        en forma de TEXTO, separados por "•"
        '''
        try:
            dia = int(dia)  # Convertir dia y mes a entero porsiacaso
            mes = int(mes)

            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT texto FROM recordatorios
                    WHERE usr_id = ? AND dia = ? AND mes = ?
                ''', (self._usr, dia, mes))
                conn.commit()           
                
                resultados = [row[0] for row in cursor.fetchall()]
                
                return ' • '.join(resultados) if resultados else None
        
        except (sqlite3.Error, ValueError) as e:
            return False

    def completamiento(self, _id: int, completo: int = 1) -> tuple[str,int]:
        '''
        se hace desde el _id del recordatorios.
        Tambien puede descomplaterase

        :param _id: id del recordatorios
        :param completo: 0 para incompleto, 1 para compelto. Default 1
        '''
        try:
            _id = int(_id)
            completo = int(completo)

            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # en caso de que se indique completo o no
                if completo == 1:
                    cursor.execute('''
                        UPDATE recordatorios
                        SET completo = 1
                        WHERE id = ?
                    ''', (_id,))
                    conn.commit()
                
                if completo != 1:
                    cursor.execute('''
                        UPDATE recordatorios
                        SET completo = ?
                        WHERE id = ?
                    ''', (completo, _id,))
                    conn.commit()
                
                # extraemos el texto del recordatorio para el return
                cursor.execute('''
                    SELECT texto FROM recordatorios
                    WHERE id = ?
                    ''', (_id,))
                conn.commit()
                
            row = cursor.fetchone()
            
            if not row:
                return False, 404
            
            texto_recordatorio = row[0]
            return texto_recordatorio, 0
                
        except sqlite3.Error as e:
            return f'Error al marcar como completado: {e}', 404
    
    def descompletar_todo(self) -> tuple[str,int]:
        '''
        todo los recordatorios del usuario
        se marcan como incompletos
        '''
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE recordatorios
                    SET completo = 0
                    WHERE usr_id = ?
                ''', (self._usr,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return False, 404
                
                return True, 0

        except sqlite3.Error as e:
            return f'Error al marcar como descompletado: {e}', 404


# %%
