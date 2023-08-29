class RPCClient {
    constructor(socket) {
        this.socket = socket;
        this.methods = {};
    }
    register(name, method) {
        this.methods[name] = method;
    }
    remove(name) {
        delete this.methods[name];
    }
    start() {
        // TODO: Is there a better way for this?
        // We create a local variable called self, so we can access the
        // `this` variable within the nested function.
        // Otherwise the `this` variable referes to the `start` function,
        // which is also an object in JS
        let self = this;
        this.socket.on(
            'rpcrequest',
            function(params) {
                let success = true;
                let result = null;
                try {
                    // Try to execute the method that was defined in
                    // rpcrequest
                    result = self.methods[params.method](params.args);
                } catch (error) {
                    success = false;
                    result = error;
                }
                self.socket.emit("rpcresponse", { success: success, result: result, id: params.id });
            }
        );
    }
}

class PubSubClient {
    constructor(socket) {
        this.socket = socket;
        this.events = {};

        socket.on(
            'pubsub',
            function(event_trigger) {
                if (this.events[event_trigger.event])
                    this.events[event_trigger.event](event_trigger.params);
            }
        );
    }
    on_event(event, method) {
        this.events[event] = method;
    }
    emit_event(event, params) {
        this.socket.emit(
            'pubsub',
            {
                event: event,
                params: params
            }
        );
    }
}

function main() {
    // io --> https://socket.io/docs/v4/client-api/
    const socket = io(location.protocol + '//' + document.domain + ':' + location.port);
    const rpcclient = new RPCClient(socket);
    rpcclient.register('initInfra3d', initInfra3d);
    rpcclient.register('lookAt2DPosition', lookAt2DPosition);
    rpcclient.register('setOnPositionChanged', setOnPositionChanged);
    rpcclient.register('unsetOnPositionChanged', unsetOnPositionChanged);
    rpcclient.start();

    const pubsubClient = new PubSubClient(socket);
    pubsubClient.emit_event("loaded", {});

    function initInfra3d(params) {
        console.log("Initializing Infra3d...");
        infra3d.init(
            "infra3d",
            params.url,
            {
                "lang" : params.lang,
                "map" : params.map,
                "layer" : params.layer,
                "navigation" : params.navigation,
                "buttons": params.buttons,
                "credentials": [params.username, params.password],
            },
            function() { pubsubClient.emit_event("initialized", {}); },
            this
        );
        return 0;
    }

    function lookAt2DPosition(params) {
        infra3d.lookAt2DPosition(params.easting, params.northing);
        return 0;
    }

    function setOnPositionChanged(_) {
        infra3d.setOnPositionChanged(
            function(
                easting, northing, height, epsg, orientation, framenumber,
                cameraname, cameratype, date, address, campaign) {
                var params = {
                    easting: easting,
                    northing: northing,
                    height: height,
                    epsg: epsg,
                    orientation: orientation,
                    framenumber: framenumber,
                    cameraname: cameraname,
                    cameratype: cameratype,
                    date: date,
                    address: address,
                    campaign: campaign
                };

                pubsubClient.emit_event("positionChanged", params);
            },
            this
        );
        return 0;
    }

    function unsetOnPositionChanged(_, _) {
        infra3d.unsetOnPositionChanged();
    }
};

main();