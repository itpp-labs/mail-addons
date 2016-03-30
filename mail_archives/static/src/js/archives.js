odoo.define('mail_archives.archives', function (require) {
"use strict";

// var core = require('web.core');
// var utils = require('web.utils');
// var Widget = require('web.Widget');

var bus = require('bus.bus').bus;
var core = require('web.core');
var data = require('web.data');
var chat_manager = require('mail.chat_manager');
var session = require('web.session');
var time = require('web.time');

var _t = core._t;
var LIMIT = 100;

var Model = require('web.Model');
var MessageModel = new Model('mail.message', session.context);

// Private model
//----------------------------------------------------------------------------------
var messages = [];
var channels = [];
var chat_unread_counter = 0;
var unread_conversation_counter = 0;
var needaction_counter = 0;
var mention_partner_suggestions = [];
var emojis = [];
var emoji_substitutions = {};
var discuss_ids = {};
var client_action_open = false;

function parse_and_transform(html_string, transform_function) {
    var open_token = "OPEN" + Date.now();
    var string = html_string.replace(/&lt;/g, open_token);
    var children = $('<div>').html(string).contents();
    return _parse_and_transform(children, transform_function)
                .replace(new RegExp(open_token, "g"), "&lt;");
}

function _parse_and_transform(nodes, transform_function) {
    return _.map(nodes, function (node) {
        return transform_function(node, function () {
            return _parse_and_transform(node.childNodes, transform_function);
        });
    }).join("");
}

// suggested regexp (gruber url matching regexp, adapted to js, see https://gist.github.com/gruber/8891611)
var url_regexp = /\b((?:https?:\/\/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/gi;
function add_link (node, transform_children) {
    if (node.nodeType === 3) {  // text node
        return node.data.replace(url_regexp, function (url) {
            var href = (!/^(f|ht)tps?:\/\//i.test(url)) ? "http://" + url : url;
            return '<a target="_blank" href="' + href + '">' + url + '</a>';
        });
    }
    if (node.tagName === "A") return node.outerHTML;
    node.innerHTML = transform_children();
    return node.outerHTML;
}

// Message and channel manipulation helpers
//----------------------------------------------------------------------------------

// options: channel_id, silent
function add_message (data, options) {
    options = options || {};
    var msg = _.findWhere(messages, { id: data.id });
    if (!msg) {
        msg = make_message(data);
        // Keep the array ordered by id when inserting the new message
        messages.splice(_.sortedIndex(messages, msg, 'id'), 0, msg);
        _.each(msg.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                add_to_cache(msg, []);
                if (options.domain && options.domain !== []) {
                    add_to_cache(msg, options.domain);
                }
                if (channel.hidden) {
                    channel.hidden = false;
                    chat_manager.bus.trigger('new_channel', channel);
                }
                if (channel.type !== 'static' && !msg.is_author && !msg.is_system_notification) {
                    if (options.increment_unread) {
                        update_channel_unread_counter(channel, channel.unread_counter+1);
                    }
                    if (channel.is_chat && options.show_notification) {
                        if (!client_action_open && config.device.size_class !== config.device.SIZES.XS) {
                            // automatically open chat window
                            chat_manager.bus.trigger('open_chat', channel, { passively: true });
                        }
                        var query = {is_displayed: false};
                        chat_manager.bus.trigger('anyone_listening', channel, query);
                        // notify_incoming_message(msg, query);
                    }
                }
            }
        });
        if (!options.silent) {
            chat_manager.bus.trigger('new_message', msg);
        }
    } else if (options.domain && options.domain !== []) {
        add_to_cache(msg, options.domain);
    }
    return msg;
}

function make_message (data) {
    var msg = {
        id: data.id,
        author_id: data.author_id,
        body_short: data.body_short || "",
        body: data.body || "",
        date: moment(time.str_to_datetime(data.date)),
        message_type: data.message_type,
        subtype_description: data.subtype_description,
        is_author: data.author_id && data.author_id[0] === session.partner_id,
        is_note: data.is_note,
        is_system_notification: data.message_type === 'notification' && data.model === 'mail.channel',
        attachment_ids: data.attachment_ids,
        subject: data.subject,
        email_from: data.email_from,
        record_name: data.record_name,
        tracking_value_ids: data.tracking_value_ids,
        channel_ids: data.channel_ids,
        model: data.model,
        res_id: data.res_id,
        url: session.url("/mail/view?message_id=" + data.id),
    };

    _.each(_.keys(emoji_substitutions), function (key) {
        var escaped_key = String(key).replace(/([.*+?=^!:${}()|[\]\/\\])/g, '\\$1');
        var regexp = new RegExp("(?:^|\\s|<[a-z]*>)(" + escaped_key + ")(?=\\s|$|</[a-z]*>)", "g");
        msg.body = msg.body.replace(regexp, ' <span class="o_mail_emoji">'+emoji_substitutions[key]+'</span> ');
    });

    function property_descr(channel) {
        return {
            enumerable: true,
            get: function () {
                return _.contains(msg.channel_ids, channel);
            },
            set: function (bool) {
                if (bool) {
                    add_channel_to_message(msg, channel);
                } else {
                    msg.channel_ids = _.without(msg.channel_ids, channel);
                }
            }
        };
    }

    Object.defineProperties(msg, {
        is_starred: property_descr("channel_starred"),
        is_needaction: property_descr("channel_inbox"),
        is_archive: property_descr("channel_archive"),
    });

    if (_.contains(data.needaction_partner_ids, session.partner_id)) {
        msg.is_needaction = true;
    }
    if (_.contains(data.starred_partner_ids, session.partner_id)) {
        msg.is_starred = true;
    }
    msg.is_archive = true;
    if (msg.model === 'mail.channel') {
        var real_channels = _.without(msg.channel_ids, 'channel_inbox', 'channel_starred', 'channel_archive');
        var origin = real_channels.length === 1 ? real_channels[0] : undefined;
        var channel = origin && chat_manager.get_channel(origin);
        if (channel) {
            msg.origin_id = origin;
            msg.origin_name = channel.name;
        }
    }

    // Compute displayed author name or email
    if ((!msg.author_id || !msg.author_id[0]) && msg.email_from) {
        msg.mailto = msg.email_from;
    } else {
        msg.displayed_author = msg.author_id && msg.author_id[1] ||
                               msg.email_from || _t('Anonymous');
    }

    // Don't redirect on author clicked of self-posted messages
    msg.author_redirect = !msg.is_author;

    // Compute the avatar_url
    if (msg.author_id && msg.author_id[0]) {
        msg.avatar_src = "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
    } else if (msg.message_type === 'email') {
        msg.avatar_src = "/mail/static/src/img/email_icon.png";
    } else {
        msg.avatar_src = "/mail/static/src/img/smiley/avatar.jpg";
    }

    // add anchor tags to urls
    msg.body = parse_and_transform(msg.body, add_link);

    // Compute url of attachments
    _.each(msg.attachment_ids, function(a) {
        a.url = '/web/content/' + a.id + '?download=true';
    });

    return msg;
}

function add_channel_to_message (message, channel_id) {
    message.channel_ids.push(channel_id);
    message.channel_ids = _.uniq(message.channel_ids);
}

function add_channel (data, options) {
    options = typeof options === "object" ? options : {};
    var channel = chat_manager.get_channel(data.id);
    if (channel) {
        if (channel.is_folded !== (data.state === "folded")) {
            channel.is_folded = (data.state === "folded");
            chat_manager.bus.trigger("channel_toggle_fold", channel);
        }
    } else {
        channel = chat_manager.make_channel(data, options);
        channels.push(channel);
        channels = _.sortBy(channels, function (channel) { return channel.name.toLowerCase(); });
        if (!options.silent) {
            chat_manager.bus.trigger("new_channel", channel);
        }
        if (channel.is_detached) {
            chat_manager.bus.trigger("open_chat", channel);
        }
    }
    return channel;
}

function get_channel_cache (channel, domain) {
    var stringified_domain = JSON.stringify(domain || []);
    if (!channel.cache[stringified_domain]) {
        channel.cache[stringified_domain] = {
            all_history_loaded: false,
            loaded: false,
            messages: []
        };
    }
    return channel.cache[stringified_domain];
}

function add_to_cache(message, domain) {
    _.each(message.channel_ids, function (channel_id) {
        var channel = chat_manager.get_channel(channel_id);
        if (channel) {
            var channel_cache = get_channel_cache(channel, domain);
            var index = _.sortedIndex(channel_cache.messages, message, 'id');
            if (channel_cache.messages[index] !== message) {
                channel_cache.messages.splice(index, 0, message);
            }
        }
    });
}

function fetch_from_channel (channel, options) {
    options = options || {};
    var domain =
        (channel.id === "channel_inbox") ? [['needaction', '=', true]] :
        (channel.id === "channel_starred") ? [['starred', '=', true]] :
        (channel.id === "channel_archive") ? [] :
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

        _.each(msgs, function (msg) {
            add_message(msg, {channel_id: channel.id, silent: true, domain: options.domain});
        });
        var channel_cache = get_channel_cache(channel, options.domain || []);
        return channel_cache.messages;
    });
}

function update_channel_unread_counter (channel, counter) {
    if (channel.unread_counter > 0 && counter === 0) {
        unread_conversation_counter = Math.max(0, unread_conversation_counter-1);
    } else if (channel.unread_counter === 0 && counter > 0) {
        unread_conversation_counter++;
    }
    if (channel.is_chat) {
        chat_unread_counter = Math.max(0, chat_unread_counter - channel.unread_counter + counter);
    }
    channel.unread_counter = counter;
    chat_manager.bus.trigger("update_channel_unread_counter", channel);
}

chat_manager.make_message = make_message;

chat_manager.get_channel = function (id) {
    return _.findWhere(channels, {id: id});
};

chat_manager.get_messages = function (options) {
    var channel;

    if ('channel_id' in options && options.load_more) {
        // get channel messages, force load_more
        channel = this.get_channel(options.channel_id);
        return fetch_from_channel(channel, {domain: options.domain || {}, load_more: true});
    }
    if ('channel_id' in options) {
        // channel message, check in cache first
        channel = this.get_channel(options.channel_id);
        var channel_cache = get_channel_cache(channel, options.domain);
        if (channel_cache.loaded) {
            return $.when(channel_cache.messages);
        } else {
            return fetch_from_channel(channel, {domain: options.domain});
        }
    }
    if ('ids' in options) {
        // get messages from their ids (chatter is the main use case)
        return fetch_document_messages(options.ids, options).then(function(result) {
            chat_manager.mark_as_read(options.ids);
            return result;
        });
    }
    if ('model' in options && 'res_id' in options) {
        // get messages for a chatter, when it doesn't know the ids (use
        // case is when using the full composer)
        var domain = [['model', '=', options.model], ['res_id', '=', options.res_id]];
        MessageModel.call('message_fetch', [domain], {limit: 30}).then(function (msgs) {
            return _.map(msgs, add_message);
        });
    }
};

chat_manager.toggle_star_status = function (message_id) {
    var msg = _.findWhere(messages, { id: message_id });
    return MessageModel.call('set_message_starred', [[message_id], !msg.is_starred]);
};
    
chat_manager.mark_channel_as_seen = function (channel) {
    if (channel.unread_counter > 0 && channel.type !== 'static') {
        update_channel_unread_counter(channel, 0);
        channel_seen(channel);
    }
};

chat_manager.mark_all_as_read = function (channel, domain) {
    if ((channel.id === "channel_inbox" && needaction_counter) || (channel && channel.needaction_counter)) {
        return MessageModel.call('mark_all_as_read', [], {channel_ids: channel.id !== "channel_inbox" ? [channel.id] : [], domain: domain});
    }
    return $.when();
};

chat_manager.bus.on('client_action_open', null, function (open) {
    client_action_open = open;
});


// Initialization
// ---------------------------------------------------------------------------------
function init () {
    add_channel({
        id: "channel_inbox",
        name: _t("Inbox"),
        type: "static"
    }, { display_needactions: true });

    add_channel({
        id: "channel_starred",
        name: _t("Starred"),
        type: "static"
    });

    add_channel({
        id: "channel_archive",
        name: _t("Archive"),
        type: "static"
    });

    var load_channels = session.rpc('/mail/client_action').then(function (result) {
        _.each(result.channel_slots, function (channels) {
            _.each(channels, add_channel);
        });
        needaction_counter = result.needaction_inbox_counter;
        mention_partner_suggestions = result.mention_partner_suggestions;
    });

    var load_emojis = session.rpc("/mail/chat_init").then(function (result) {
        emojis = result.emoji;
        _.each(emojis, function(emoji) {
            emoji_substitutions[_.escape(emoji.source)] = emoji.substitution;
        });
    });

    var ir_model = new Model("ir.model.data");
    var load_menu_id = ir_model.call("xmlid_to_res_id", ["mail.mail_channel_menu_root_chat"], {}, {shadow: true});
    var load_action_id = ir_model.call("xmlid_to_res_id", ["mail.mail_channel_action_client_chat"], {}, {shadow: true});

    // bus.on('notification', null, on_notification);

    return $.when(load_menu_id, load_action_id, load_channels, load_emojis).then(function (menu_id, action_id) {
        discuss_ids = {
            menu_id: menu_id,
            action_id: action_id
        };
        bus.start_polling();
    });
}


chat_manager.is_ready = init();
return chat_manager;

});
