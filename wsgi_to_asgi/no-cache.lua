-- wrk_cache_bypass.lua
wrk.method = "GET"
wrk.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
wrk.headers["Pragma"] = "no-cache"
wrk.headers["Expires"] = "0"
request = function()
    -- Adding a unique query parameter to ensure each request looks unique
    local unique_id = math.random(1000000)
    local path = wrk.path .. "?nocache=" .. unique_id
    return wrk.format(nil, path)

end

