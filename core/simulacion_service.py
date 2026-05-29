"""core/simulacion_service.py - Servicio que orquesta la simulación completa."""

from typing import Callable

from core.gcl import GeneradorCongruencialLineal
from core.parametros import ParametrosSistema
from core.resultados import ResultadoLote


class SimulacionService:
    """
    Servicio de simulación que orquesta todos los componentes.
    Implementa el flujo general de simulación basado en el diagrama.
    """

    def __init__(
        self,
        parametros: ParametrosSistema,
        gcl_factory: Callable[[], GeneradorCongruencialLineal] = None,
    ):
        """
        Inicializa el servicio de simulación.

        Args:
            parametros: ParametrosSistema compartido con la aplicación.
            gcl_factory: Factory para crear GeneradorCongruencialLineal.
        """
        self.parametros = parametros
        self.gcl_factory = gcl_factory or GeneradorCongruencialLineal

    def _procesar_material(self, resultado: ResultadoLote, p: float):
        """Aplica las fórmulas del subdiagrama de Recuperación de Material."""
        cobre = p * 0.2
        aluminio = p * 0.03
        oro = p * 0.01
        plastico = p * 0.6
        
        resultado.peso_cobre += cobre
        resultado.peso_aluminio += aluminio
        resultado.peso_oro += oro
        resultado.peso_plastico += plastico
        resultado.peso_metal += (cobre + aluminio + oro)
        
        vc = cobre * 8500
        va = aluminio * 1500
        vo = oro * 210000
        vp = plastico * 60
        
        resultado.valor_cobre += vc
        resultado.valor_aluminio += va
        resultado.valor_oro += vo
        resultado.valor_plastico += vp
        
        vm = vc + va + vo
        resultado.pmt += vm
        resultado.pt += vp

    def simular_lote(self, n_total: int) -> ResultadoLote:
        """
        Ejecuta la simulación completa de un lote de dispositivos.
        Sigue estrictamente el flujo del diagrama general.

        Args:
            n_total: Cantidad de dispositivos del lote.

        Returns:
            ResultadoLote con agregados y métricas.
        """
        if not self.parametros.parametros_cargados:
            raise RuntimeError(
                "Los parámetros operativos no han sido cargados. "
                "Por favor, complete la Vista del Gerente antes de ejecutar."
            )

        gcl = self.gcl_factory()
        resultado = ResultadoLote()
        resultado.semilla_gcl = gcl.semilla
        resultado.n_total = n_total

        # Bucle central I = 1 a N_total
        for _ in range(n_total):
            # Estación 1: Revisión General (Exponencial media 3 min)
            e1 = gcl.siguiente_exponencial(3.0)
            resultado.c1 += 1
            resultado.tdr += e1

            # Revisión: ¿Funciona bien? (Reventa 25%)
            if gcl.siguiente_u() < 0.25:
                resultado.equipos_reventa += 1
                # Separar en tipo (DVR 11.3%)
                if gcl.siguiente_u() < 0.113:
                    resultado.dvrs_reventa += 1
                else:
                    resultado.camaras_reventa += 1
                continue  # Pasa al siguiente dispositivo, no se desguaza

            # Procesar / Tratar (Desguace)
            if gcl.siguiente_u() < 0.113:
                # Es DVR
                resultado.dvrs_desguazados += 1
                p = gcl.siguiente_rango(0.8, 2.0)  # Peso estimado DVR Uniforme
                resultado.mt += p
                
                # Estación 5: DVR Desarme General
                d5 = gcl.siguiente_exponencial(10.0)
                resultado.c5 += 1
                resultado.tdd += d5
                
                # HDD Sano (0.68) o Roto
                resultado.hdd_t += 1
                if gcl.siguiente_u() < 0.68:
                    # Sano: N = 250 + 1750*U (Uniforme 250 a 2000 GB)
                    _ = gcl.siguiente_rango(250, 2000)
                    resultado.hdd_f += 1
                else:
                    # Roto: Estación 6 (HDD Desguace Material)
                    d6 = gcl.siguiente_exponencial(3.0)
                    resultado.c6 += 1
                    resultado.thd += d6
                
                # Placas Sanas (0.27) o Rotas
                resultado.placas_t += 1
                if gcl.siguiente_u() < 0.27:
                    resultado.placas_f += 1  # Sana
                else:
                    # Rota: Estación 4 (Placas Desguace)
                    d4 = gcl.siguiente_exponencial(0.5)
                    resultado.c4 += 1
                    resultado.tp += d4
                
                self._procesar_material(resultado, p)

            else:
                # Es Cámara
                resultado.camaras_desguazadas += 1
                p = gcl.siguiente_rango(0.2, 1.5)  # Peso Cámara Uniforme
                resultado.mt += p
                
                # Estación 2: Cámara Desarme Óptica
                d2 = gcl.siguiente_exponencial(2.0)
                resultado.c2 += 1
                resultado.tdo += d2
                
                # Óptica Sana (0.70) o Rota
                if gcl.siguiente_u() < 0.70:
                    resultado.peso_vidrio += (p * 0.3)  # Sana
                else:
                    # Rota: Estación 3 (Óptica Material)
                    d3 = gcl.siguiente_exponencial(2.0)
                    resultado.c3 += 1
                    resultado.tco += d3
                
                # Placas Sanas (0.52) o Rotas
                resultado.placas_t += 1
                if gcl.siguiente_u() < 0.52:
                    resultado.placas_f += 1  # Sana
                else:
                    # Rota: Estación 4 (Placas Desguace)
                    d4 = gcl.siguiente_exponencial(0.5)
                    resultado.c4 += 1
                    resultado.tp += d4
                
                self._procesar_material(resultado, p)

        # Cálculo de Ocupaciones / Eficiencia y Cuellos de Botella (OE > 0.85)
        # Se calcula asumiendo el tiempo real vs el tiempo esperado si estuviera 100% ocupado.
        resultado.pe1 = (resultado.tdr / (resultado.c1 * 3.0)) if resultado.c1 > 0 else 0
        if resultado.pe1 > 0.85:
            resultado.cuellos_botella.append("Estación 1 (Revisión)")
            
        resultado.pe2 = (resultado.tdo / (resultado.c2 * 2.0)) if resultado.c2 > 0 else 0
        if resultado.pe2 > 0.85:
            resultado.cuellos_botella.append("Estación 2 (Óptica)")
            
        resultado.pe3 = (resultado.tco / (resultado.c3 * 2.0)) if resultado.c3 > 0 else 0
        if resultado.pe3 > 0.85:
            resultado.cuellos_botella.append("Estación 3 (Óptica Material)")
            
        resultado.pe4 = (resultado.tp / (resultado.c4 * 0.5)) if resultado.c4 > 0 else 0
        if resultado.pe4 > 0.85:
            resultado.cuellos_botella.append("Estación 4 (Placas)")
            
        resultado.pe5 = (resultado.tdd / (resultado.c5 * 10.0)) if resultado.c5 > 0 else 0
        if resultado.pe5 > 0.85:
            resultado.cuellos_botella.append("Estación 5 (DVR)")
            
        resultado.pe6 = (resultado.thd / (resultado.c6 * 3.0)) if resultado.c6 > 0 else 0
        if resultado.pe6 > 0.85:
            resultado.cuellos_botella.append("Estación 6 (HDD)")

        # Simulación de Demanda (Poisson)
        # Calcula horas necesarias (h) para vender/procesar todo el lote 
        # asumiendo una demanda de 0.3 clientes por hora.
        h = 0
        cp = 0
        # Ponemos un límite por seguridad en caso de N_total gigantesco para que no cuelgue
        while cp < n_total and h < 1000000:
            cl = gcl.siguiente_poisson(0.3)
            cp += cl
            h += 1
            
        resultado.horas_demanda = h
        resultado.clientes_totales = cp

        return resultado
