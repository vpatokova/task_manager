const second = 1000
const minute = 60
const hour = 60 * 60
const day = 60 * 60 * 24

function toMilliseconds(rowTime) {
    let [hours, minutes, seconds] = rowTime.split(":")

    return (
        Number(hours) * hour +
        Number(minutes) * minute +
        Number(seconds)
    ) * second
}

function extractElement(node, className) {
    return node.children(className).get(0)
}

function parse() {
    let tasksList = $(".task")

    let timers = []

    for (let node of tasksList) {
        node = $(node)
        const id = extractElement(
            node, ".task_id"
        )
        const time = extractElement(
            node, ".task_time"
        )
        const timeBreak = extractElement(
            node, ".task_time_to"
        )
        const statusElement = extractElement(
            node, ".task_status"
        )
        const facade = extractElement(
            node, ".task_button_td"
        )
        const inner = extractElement(
            $(facade), ".task_button_facade"
        )
        const button = extractElement(
            $(inner), ".task_button_resume"
        )

        timers.push(
            new Timer(
                id.innerText,
                statusElement,
                time,
                timeBreak,
                button
            )
        )
    }

    return timers
}

class Timer {
    constructor(id, statusElement, timeElement, timeBreakElement, button) {
        this.id = id
        this.statusElement = statusElement
        this.timeBreakElement = timeBreakElement
        this.timeElement = timeElement
        this.isCompleted = false
        this.button = button
        this.status = null
    }

    update(response) {
        const statusText = response['status_text']
        this.changeStatus(statusText)

        if (this.isCompleted) {
            this.setEmptyMainTimer()
            this.setEmptyBreakTimer()
            this.button.className = "btn btn-primary task_button_resume disabled"
            return
        }

        let timedelta = response['remaining_time']
        this.updateTimer(timedelta, this.timeElement)

        const isWithBreaks = Boolean(response['is_with_breaks'])
        const status = response['status']

        if (toMilliseconds(timedelta) <= 0) {
            this.setEmptyMainTimer()
            this.setEmptyBreakTimer()
            this.isCompleted = true
            this.button.className = "btn btn-primary task_button_resume disabled"
            return
        }
        if(status === "completed" || !isWithBreaks) {
            this.setEmptyBreakTimer()
            return
        }
        if (this.timeBreakElement !== undefined) {
            this.updateTimer(response['time_to'], this.timeBreakElement)
        }
        if (this.statusElement !== undefined) {
            this.changeStatus(statusText)
        }
    }

    setEmptyBreakTimer() {
        if (this.timeBreakElement !== undefined) {
            this.timeBreakElement.innerText = ""
        }
    }

    setEmptyMainTimer() {
        if (this.timeElement !== undefined) {
            this.timeElement.innerText = ""
        }
    }

    changeStatus(status) {
        this.statusElement.innerText = status
    }

    updateTimer(timedelta, element) {
        if (isNaN(toMilliseconds(timedelta))) {
            return
        }

        element.innerText = timedelta
    }
}

const timers = parse()
const timerByTaskId = {}
let stopTasks = false;

for (const timer of timers) {
    timerByTaskId[timer.id] = timer
}

const intervalId = setInterval(() => {
    $.ajax({
        url: `/tasks/time/`,
        method: 'get',
        dataType: 'json',
        success: (response, status, _) => {
            let statuses = []
            for (let taskInfo of response) {
                let task = timerByTaskId[taskInfo['task_id']]
                task.update(taskInfo)
                statuses.push(toMilliseconds(taskInfo['remaining_time']) >= 0)
                task.update(taskInfo)
            }
            if (stopTasks) {
                clearInterval(intervalId)
            }
            stopTasks = !statuses.some(Boolean)
        }
    })
},1000)
