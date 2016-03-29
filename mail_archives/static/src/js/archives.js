odoo.define('mail_archives.archives', function (require) {
"use strict";

// var core = require('web.core');
// var utils = require('web.utils');
// var Widget = require('web.Widget');
var Model = require('web.Model');
var MessageModel = new Model('mail.message', session.context);

var chat_manager = require('mail.chat_manager');
console.log('qqq');

var LIMIT = 100;

function get_channel_cache (channel, domain) {
    var stringified_domain = JSON.stringify(domain || []);
    if (!channel.cache[stringified_domain]) {
        channel.cache[stringified_domain] = {
            all_history_loaded: false,
            loaded: false,
            messages: [],
        };
    }
    return channel.cache[stringified_domain];
}

function fetch_from_channel (channel, options) {
    options = options || {};
    var domain =
        (channel.id === "channel_inbox") ? [['needaction', '=', true]] :
        (channel.id === "channel_starred") ? [['starred', '=', true]] :
        (channel.id === "channel_archive") ? [['read', '=', true]] :
                                            [['channel_ids', 'in', channel.id]];
    var cache = get_channel_cache(channel, options.domain);

    if (options.domain) {
        domain = new data.CompoundDomain(domain, options.domain || []);
    }
    if (options.load_more) {
        var min_message_id = cache.messages[0].id;
        domain = new data.CompoundDomain([['id', '<', min_message_id]], domain);
    }

    return MessageModel.call('message_fetch', [domain], {limit: LIMIT}).then(function (msgs) {
        if (!cache.all_history_loaded) {
            cache.all_history_loaded =  msgs.length < LIMIT;
        }
        cache.loaded = true;

        // _.each(msgs, function (msg) {
        //     add_message(msg, {channel_id: channel.id, silent: true, domain: options.domain});
        // });
        var channel_cache = get_channel_cache(channel, options.domain || []);
        return channel_cache.messages;
    });
}

//TODO: переложить все в репозиторий mail_addons-9.0-res_partner_mails_count
return chat_manager;

});
