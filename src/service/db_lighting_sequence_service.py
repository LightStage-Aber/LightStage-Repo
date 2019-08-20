import json, copy
import backoff, threading, logging

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


from db_access import DBADO_ThreadedPubSub
from sequences import GradientSequence_IntervalSpecified


class NoDataYet(Exception): pass


"""
    ------------------------------------------------------------------------
    -- Data Service Client --
    ------------------------------------------------------------------------ 
"""


class DataService_Client_SphericalGradient(DBADO_ThreadedPubSub):
    """
        Data Service for supplying spherical gradient lighting sequences.

            - This uses Pubsub to permit requests from API/HTTP clients.
            - This lets API/HTTP clients request/specify their own sequence variants.
            - Pubsub requires publish() from the WS.
            - Pubsub requires subscribe() from the application.
            - subscribe() will execute WS's published request and set() result into redis.
            - WS will request result data in redis via lookup().

            Data Service has two use cases. Run by Client. Run by Server.
            Function call access are separated in classes.

            This is the Client-side Data Service.

            WS Client calls to:
            - lookup() - get/check sequence data
            - publish() - request new sequence data
            - lookup_and_wait() - get/check sequence data, wait for it to be available.
    """

    def __init__(self, *args, **kwords):
        DBADO_ThreadedPubSub.__init__(self, *args, **kwords)
        self._namespace_pubsub = "pubsub.SphericalGradient"
        self._sphericalGradient_data = "sphericalgradient_data"

    def publish_to_service(self, axis, num_rotations, current_rotation):
        data = Extractor.apply(axis, num_rotations, current_rotation)
        json_data = json.dumps( data, separators=(',',':') )
        return self.publish( self._namespace_pubsub, json_data )
            
    def lookup(self, axis, num_rotations, current_rotation):
        key = KeyFormatter.apply(self._sphericalGradient_data, axis, num_rotations, current_rotation)
        json_data = self.get( key )
        json_data = json_data if json_data is not None else ""
        return json.dumps( json_data )

    @backoff.on_exception(backoff.fibo,
                      NoDataYet,
                      max_time=10)
    def lookup_and_wait(self, axis, num_rotations, current_rotation):
        key = KeyFormatter.apply(self._sphericalGradient_data, axis, num_rotations, current_rotation)
        json_data = self.get( key )
        if json_data is None:
            raise NoDataYet()
        return json.dumps( json_data )




"""
    ------------------------------------------------------------------------
    -- Data Service Server --
    ------------------------------------------------------------------------ 
"""

class DataService_Server_SphericalGradient(DBADO_ThreadedPubSub):
    """
        Data Service for supplying spherical gradient lighting sequences.

            - This uses Pubsub to permit requests from API/HTTP clients.
            - This lets API/HTTP clients request/specify their own sequence variants.
            - Pubsub requires publish() from the WS.
            - Pubsub requires subscribe() from the application.
            - subscribe() will execute WS's published request and set() result into redis.
            - WS will request result data in redis via lookup().

            Data Service has two use cases. Run by Client. Run by Server.
            Function call access are separated in classes.
            
            This is the Server-side Data Service. Its subscription processing is multi-threaded and locks on `__frozen` shared data.

            Application Server calls to:
            - subscribe() - listen for new sequence data request
            - __callback_func
            - [super].set_series()   - set new sequence data
    """

    __frozen = None
    __frozen_lock = threading.Lock()

    def __init__(self, leds_vertices, led_indexes, intensities, *args, **kwords):
        DBADO_ThreadedPubSub.__init__(self, *args, **kwords)
        self._namespace_pubsub = "pubsub.SphericalGradient"
        self._sphericalGradient_data = "sphericalgradient_data"
        self.frame_obj = LightFrameData( leds_vertices, led_indexes, intensities )
        DataService_Server_SphericalGradient.__set_frozen_data( self )

    @staticmethod
    def __set_frozen_data( d ):
        if DataService_Server_SphericalGradient.__frozen is None:
            with DataService_Server_SphericalGradient.__frozen_lock:
                if DataService_Server_SphericalGradient.__frozen is None:
                    #
                    # --- Set value.
                    logging.info("Frozen: {} ---- {} ".format(repr(d), dir(d)))
                    DataService_Server_SphericalGradient.__frozen = d
                    #DataService_Server_SphericalGradient.__frozen = super(DataService_Server_SphericalGradient, cls).__new__(cls)

    @staticmethod
    def __get_frozen_data():
        data = None
        # --- get value.
        data = DataService_Server_SphericalGradient.__frozen
        logging.info("Frozen: {} ---- {} ".format(repr(data), dir(data)))
        return data

    def subscribe_to_service(self):
        self.subscribe( self._namespace_pubsub, self.__callback_func )

    def __callback_func(self, msg):
        # .. may have to json.loads() msg first..
        obj = DataService_Server_SphericalGradient.__get_frozen_data()
        assert obj is not None, "Server data object from frozen should be valid before processing new request for lighting sequence."
        resultset = ProcessRequest.process(msg,  obj)
        self.set_series( resultset )         # 5. set each requested sequence into redis.
        






"""
    ========================================================================

    -- Helpers --

    ======================================================================== 
"""

class ProcessRequest:


    @staticmethod
    def process(msg, server_obj):
        assert server_obj is not None, "Requests for new lighting sequences require valid server data object."
        assert msg is not None, "Requests for new lighting sequences require valid pubsub message object."
        resultset = {}
        # 1. valdiate data msg.
        res = ProcessRequest._validate(msg, server_obj)
        is_valid = isinstance(res, Iterable)

        if is_valid:
            (axis, num_rotations, current_rotation) = res
            # 2. data = recreate gradient lighting obj
            logging.info("Received request for {} {} {}".format(axis, num_rotations, current_rotation ))
            gs = ProcessRequest._getSequence(axis, num_rotations, server_obj)
            #until_rotations = current_rotation if current_rotation <= num_rotations else num_rotations
            #logging.info("Number of rotations {}, {}".format(until_rotations, type(until_rotations)))
            # 3. collect intensity data for each rotation 
            for i in range(num_rotations):
                ls_con = gs.get_next_sequence()
                # 4. Prepare each intensity dataset for redis -> [[led_n,int_v],..]
                intensities = [l.get_intensity() for l in ls_con]
                published_intensity_set = zip( server_obj.frame_obj.led_indexes, copy.deepcopy(intensities) )
                # 5. prepare each for insert into redis.
                # "prefix.axis.num_rotations.i-n": -> [[led_n,int_v],..]
                key = KeyFormatter.apply(server_obj._sphericalGradient_data, axis, num_rotations, i)
                value = json.dumps( published_intensity_set, separators=(',',':') )
                resultset[key] = value
                logging.info("Rotation: {} for key: {}".format(i, key))
        else:
            # ignore invalid requests.
            logging.info("Ignoring published message to "+str(server_obj._namespace_pubsub)+": data format out of scope.\n"+str(msg))
        return resultset
    
    @staticmethod
    def _validate(msg, server_obj):
        try:
            payload = json.loads(msg['data'])
            axis, num_rotations, current_rotation = Extractor.unapply( payload )
            assert axis in ["x","y","z"], "Requested axis value is not \"x,y,z\"."
            assert current_rotation == -1 or current_rotation >= 0 and current_rotation < num_rotations, "Invalid current rotation value."
            return (axis, num_rotations, current_rotation)
        except Exception as e:
            return None
    
    @staticmethod
    def _getSequence(axis, num_rotations, server_obj):
        return GradientSequence_IntervalSpecified(
            server_obj.frame_obj.leds_vertices, 
            server_obj.frame_obj.intensities, 
            axis=axis, 
            quantity_of_intervals=num_rotations)


class LightFrameData:
    def __init__(self, leds_vertices, led_indexes, intensities):
        self.leds_vertices = leds_vertices
        self.led_indexes = led_indexes
        self.intensities = intensities

class KeyFormatter:
    @staticmethod
    def apply(prefix, axis, num_rotations, current_rotation):
        # e.g. "pubsub.SphericalGradient.x.1.-1"
        return prefix+"."+str(axis)+"."+str(num_rotations)+"."+str(current_rotation)

class Extractor:
    @staticmethod
    def apply(axis, num_rotations, current_rotation):
        """
        data = Extractor.apply(axis, num_rotations, current_rotation)
        """
        return {
                "axis":axis,
                "num_rotations":num_rotations,
                "current_rotation":current_rotation
                }
    @staticmethod
    def unapply(data):
        """
        axis, num_rotations, current_rotation = Extractor.unapply(data)
        """
        def _cast( d , t ):
            # Cast from unicode to required type:
            try:
                return t(d)
            except Exception:
                return None
        return _cast(data["axis"], str), _cast(data["num_rotations"], int), _cast(data["current_rotation"], int)








# class DataService_SphericalGradient(DBADO_ThreadedPubSub):
#     """
#         Data Service for supplying spherical gradient lighting sequences.

#             - This uses Pubsub to permit requests from API/HTTP clients.
#             - This lets API/HTTP clients request/specify their own sequence variants.
#             - Pubsub requires publish() from the WS.
#             - Pubsub requires subscribe() from the application.
#             - subscribe() will execute WS's published request and set() result into redis.
#             - WS will request result data in redis via lookup().

#             Data Service has two use cases. Run by Client. Run by Server.
#             Function call access are separated in classes.

#             WS Client calls to:
#             - lookup() - get/check sequence data
#             - publish() - request new sequence data
#             - lookup_and_wait() - get/check sequence data, wait for it to be available.

#             Application Server calls to:
#             - subscribe() - listen for new sequence data request
#             - __callback_func
#             - [super].set_series()   - set new sequence data
#     """
#     pass