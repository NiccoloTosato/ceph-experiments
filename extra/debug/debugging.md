# Fio debugging

Usefull files:

- `debug.fio`: used to generate the results.
- `fio-output.json`: json report obtained running `debug.fio`.
- `fio-output.txt`: `stdout` running fio with a CLI output.

[plot here](read_bw.png)

## Json+ result

The results from json+ seems not reasonable, while increasing the process count, the bw reach unreasonable values in a single disk ~ 400 MB/s

Parse the output with `jq`, query the read bw, reported in Kibytes:

```bash
$ cat fio-output.json| jq '.jobs[17].read.bw_mean'
412250.900152
$ cat fio-output.json| jq '.jobs[17].read.bw_max'
565806

# too big numbers ... 412 MiB/s or 565 MiB/s ...

```

Query the runtime, should be *ms*, since we required to te bench to last at least 30 secs..:
```bash
$ cat fio-output.json| jq '.jobs[17].read.runtime'
30060
```

Query then the number of bytes handled: 
```bash
$ cat fio-output.json| jq '.jobs[17].read.io_bytes'
7952400384
```

Then the calcutation of the true bw shoud be: 7952400384/30.060/1024=258350.5 KiB/s. **THAT IS REASONABLE**.

**Note**: there is also a field called `bw_bytes`:
```bash
$cat fio-output.json| jq '.jobs[17].read.bw_bytes'
264550910
```
This blogpost use io_bytes to calculate the bw: [here](https://tobert.github.io/post/2014-04-17-fio-output-explained.html)

Conclusion there is an error o a misconception from my side on how the results must be parsed.
Update: **MAYBE** is my fault, seems that bw_bytes is the bandwith in bytes, ~ 264 MB/s. But why `bw_mean` is not the correct one ?!

[This issue](https://github.com/axboe/fio/issues/1134** should be related ...

**Solution**: if we normalize respect the number of jobs, we get the right result !
Look at the [Source code, line 1484](https://github.com/axboe/fio/blob/master/stat.c)

Also note the comment in the mean function:

```bash

static void __sum_stat(struct io_stat *dst, struct io_stat *src, bool first)
{
	double mean, S;

	dst->min_val = min(dst->min_val, src->min_val);
	dst->max_val = max(dst->max_val, src->max_val);

	/*
	 * Compute new mean and S after the merge
	 * <http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
	 *  #Parallel_algorithm>
	 */
	if (first) {
		mean = src->mean.u.f;
		S = src->S.u.f;
	} else {
		double delta = src->mean.u.f - dst->mean.u.f;

		mean = ((src->mean.u.f * src->samples) +
			(dst->mean.u.f * dst->samples)) /
			(dst->samples + src->samples);

		S =  src->S.u.f + dst->S.u.f + pow(delta, 2.0) *
			(dst->samples * src->samples) /
			(dst->samples + src->samples);
	}

	dst->samples += src->samples;
	dst->mean.u.f = mean;
	dst->S.u.f = S;

}

/*
 * We sum two kinds of stats - one that is time based, in which case we
 * apply the proper summing technique, and then one that is iops/bw
 * numbers. For group_reporting, we should just add those up, not make
 * them the mean of everything.
 */
```
Is this a bug ? 

## Normal result

Running `fio` in a standard way we get:
```bash
cat fio-output.txt | grep "READ: bw" | awk '{print $2}' | sort
bw=105MiB/s
bw=118MiB/s
bw=118MiB/s
bw=150MiB/s
bw=158MiB/s
bw=191MiB/s
bw=197MiB/s
bw=20.8MiB/s
bw=236MiB/s
bw=238MiB/s
bw=241MiB/s
bw=251MiB/s
bw=252MiB/s
bw=253MiB/s
bw=253MiB/s
bw=253MiB/s
bw=253MiB/s
bw=253MiB/s
bw=253MiB/s
bw=28.2MiB/s
bw=39.8MiB/s
bw=50.4MiB/s
bw=68.6MiB/s
bw=80.2MiB/s
```
So no extreme numbers and all reasonable numbers.
